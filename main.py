#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this
#  software and associated documentation files (the "Software"), to deal in the Software
#  without restriction, including without limitation the rights to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import base64
import datetime
import math

import boto3
import cv2


def parse_arguments():
    """ Parse command line arguments """
    def datetime_type(date_str):
        return datetime.datetime.fromisoformat(date_str)

    parser = argparse.ArgumentParser()
    parser.add_argument("--stream-name", required=True, help="Kinesis Video Streams stream name")
    parser.add_argument("--start-time", required=True, type=datetime_type, help="ISO format timestamp")
    parser.add_argument("--end-time", required=True, type=datetime_type, help="ISO format timestamp")
    parser.add_argument("--duration", default=5, type=int, help="duration seconds of output video")
    parser.add_argument("--framerate", default=30, type=int, help="framerate of output video")
    parser.add_argument("--width", default=1920, type=int, help="width of output video")
    parser.add_argument("--height", default=1080, type=int, help="height of output video")
    parser.add_argument("--output-path", required=True, help="path to write output video")
    args = parser.parse_args()

    # Validate arguments
    if args.end_time <= args.start_time:
        raise RuntimeError("end_time must be later than start_time")
    return args


def get_kvs_archived_media_client(stream_name):
    """ Confirm data endpoint and get boto3 client for Kinesis Video Archived Media """
    kvs = boto3.client("kinesisvideo")

    endpoint = kvs.get_data_endpoint(
        APIName="GET_IMAGES",
        StreamName=stream_name,
    )['DataEndpoint']

    kvs_am_client = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
    return kvs_am_client


def get_and_write_frame(args, kvs_am_client, timestamp, writer):
    """ Fetch a frame at the timestamp and write it to the video writer """
    try:
        res = kvs_am_client.get_images(
            StreamName=args.stream_name,
            ImageSelectorType='SERVER_TIMESTAMP',
            StartTimestamp=timestamp,
            EndTimestamp=timestamp + datetime.timedelta(seconds=3),
            SamplingInterval=3000,
            Format='JPEG',
            WidthPixels=args.width,
            HeightPixels=args.height,
            MaxResults=3,
        )
    except kvs_am_client.exceptions.ResourceNotFoundException as e:
        print(f"{e} at {timestamp}")
        return
    for image in res["Images"]:
        if "Error" not in image:
            content = image["ImageContent"]
            path = "/tmp/image.jpg"
            print(f"Write a frame at {timestamp}")
            with open(path, "wb") as fw:
                fw.write(base64.b64decode(content))

            cv2_image = cv2.imread(path)
            writer.write(cv2_image)
            return
    print(f"Couldn't find a valid image frame at {timestamp}")


def generate_video(args, kvs_am_client, writer):
    """ Generate timelapse video """
    total_frames = args.duration * args.framerate
    duration_seconds = (args.end_time - args.start_time).total_seconds()
    interval = math.ceil(duration_seconds / total_frames)
    for n in range(total_frames):
        timestamp = args.start_time + datetime.timedelta(seconds=n * interval)
        get_and_write_frame(args, kvs_am_client, timestamp, writer)


def main():
    args = parse_arguments()
    kvs_am_client = get_kvs_archived_media_client(args.stream_name)
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(args.output_path, fmt, float(args.framerate), (args.width, args.height))
    generate_video(args, kvs_am_client, writer)
    print(f"Saving video: {args.output_path}")
    writer.release()


if __name__ == '__main__':
    main()
