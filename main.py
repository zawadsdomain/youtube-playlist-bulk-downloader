from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import yt_dlp
from typing import List, Optional
import json

app = FastAPI(title = "Youtube Playlist Downloader API", description = "A simple API to download Youtube playlists")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Defining classes for request, response and video info. 

class VideoInfo(BaseModel):
    id: str
    title: str
    thumbnail: str
    duration: Optional[int]
    url: str

class PlaylistRequest(BaseModel):
    url: HttpUrl

class PlaylistResponse(BaseModel):
    playlist_title: str
    videos: List[VideoInfo]

class DownloadRequest(BaseModel):
    url: HttpUrl
    output_path: Optional[str] = "downloads"

class DownloadResponse(BaseModel):
    status: str # "success" or "error"
    message: str
    downloaded_videos: List[str]
    failed_videos: List[str]

@app.get('/')
async def root():
    return {"message": "YouTube Playlist Downloader API is running"}

@app.post('/api/fetch_playlist', response_model = PlaylistResponse) # Fetching playlist videos from Youtube
async def fetch_playlist(request: PlaylistRequest):
    try: 
        ydl_opts = {
            'quiet': True, # Suppress output
            'extract_flat': True, # Don't download videos, just get info
            'force_generic_extractor': False # Use yt-dlp's generic extractor
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            playlist_info = ydl.extract_info(str(request.url), download=False)

            if not playlist_info:
                raise HTTPException(status_code = 404, detail = "Playlist not found")
            
            # extract video info from playlist

            videos = []

            for entry in playlist_info.get('entries', []):
                if entry:
                    video_info = VideoInfo(
                        id = entry.get('id'),
                        title = entry.get('title'),
                        thumbnail = entry.get('thumbnail'),
                        duration = entry.get('duration'),
                        url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                    )
                    videos.append(video_info)

            return PlaylistResponse(
                playlist_title = playlist_info.get('title', ''),
                videos = videos
            )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@app.post('/api/download_playlist', response_model = DownloadResponse)
async def download_playlist(request: DownloadRequest):
    try:
        ydl_opts = {
            'format': 'best', # Download best quality
            'outtmpl': f'{request.output_path}/%(title)s.%(ext)s', # Output template
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False # We want to download the videos
        }

        downloaded_vids = []
        failed_vids = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(str(request.url), download=False)

            if not playlist_info:
                raise HTTPException(status_code = 404, detail = "Playlist not found")
            
            for entry in playlist_info.get('entries', []):
                if entry:
                    try:
                        video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                        ydl.download([video_url])
                        downloaded_vids.append(entry.get('title', 'Unknown Title'))
                    except Exception as e:
                        failed_vids.append(entry.get('title', 'Unknown Title'))
            
        return DownloadResponse(
            status = "success",
            message = f"Downloaded {len(downloaded_vids)} videos. {len(failed_vids)} videos failed.",
            downloaded_videos = downloaded_vids,
            failed_videos = failed_vids
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)