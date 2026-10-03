import asyncio
import dxcam

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import VideoStreamTrack
from av import VideoFrame

camera = dxcam.create(
    output_idx=0,
    output_color="RGB",
    backend="dxgi"
)

camera.start(
    target_fps=60,
    video_mode=True
)

class ScreenTrack(VideoStreamTrack):

    def __init__(self):
        super().__init__()

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = await asyncio.to_thread(
            camera.get_latest_frame,
            copy=True
        )

        video_frame = VideoFrame.from_ndarray(
            frame,
            format="rgb24"
        )

        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame