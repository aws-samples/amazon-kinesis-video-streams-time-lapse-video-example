# Amazon Kinesis Video Streams - Time Lapse Video Generation Sample

This is a sample code to generate time-lapse video from [Amazon Kinesis Video Streams](https://aws.amazon.com/kinesis/video-streams/).

## Prerequisite

- Python 3.6 or above
- opencv-python 4.5 or above
- boto3 1.22.7 or above
- A stream of Kinesis Video Streams with media ingested at that time

Python packages can be installed with `pip3 install -r requirements.txt`.

If you are not familiar with Kinesis Video Streams, you can learn [how it works](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/how-it-works.html).
If you want to learn how to ingest media into Kinesis Video Streams, you can use [Producer libraries](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/producer-sdk.html).

If you haven't configured AWS credentials for boto3, please follow [the instructions](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration).

## Usage

```bash
usage: main.py [-h] --stream-name STREAM_NAME --start-time START_TIME --end-time END_TIME
               [--duration DURATION] [--framerate FRAMERATE] [--width WIDTH] [--height HEIGHT] --output-path OUTPUT_PATH

arguments:
  -h, --help                 show this help message and exit
  --stream-name STREAM_NAME  Kinesis Video Streams stream name
  --start-time START_TIME    ISO format timestamp
  --end-time END_TIME        ISO format timestamp
  --duration DURATION        duration seconds of output video
  --framerate FRAMERATE      framerate of output video
  --width WIDTH              width of output video
  --height HEIGHT            height of output video
  --output-path OUTPUT_PATH  path to write output video
```

### Example

```bash
python3 main.py \
  --stream-name my-kvs-stream \
  --start-time 2022-01-01T00:00:00 \
  --end-time 2022-01-01T09:00:00 \
  --duration 3 \
  --width 1920 \
  --height 1080 \
  --output-path result.mp4
```

## Example Output

[result.mp4](./result.mp4)

## How it works?

This sample uses [GetImages API](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_reader_GetImages.html) to extract images from a Kinesis Video stream.
Extracted images are combined and written as a mp4 video using OpenCV.

## Note

Please confirm [Kinesis Video Streams pricing](https://aws.amazon.com/kinesis/video-streams/pricing/) before using this sample.
You will be charged for Kinesis Video Streams image generation depending on the number of images generated and its resolution.

## Links

- [Amazon Kinesis Video Streams Developer Guide](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/what-is-kinesis-video.html)
- [Amazon Kinesis Video Streams Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/b95b9381-baf0-4bef-ba31-63817d54c2a6)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
