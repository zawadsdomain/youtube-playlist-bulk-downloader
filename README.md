# YouTube Bulk Downloader API

A FastAPI-based service that allows you to fetch and download YouTube playlists in bulk. The API provides endpoints to preview playlist contents and download videos.

## Features

- Fetch playlist information including video titles, thumbnails, and durations
- Download entire playlists with a single request
- Track download progress and status
- Customizable output directory
- RESTful API interface

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python main.py
   ```

The server will start at `http://localhost:8000`

## API Endpoints

### GET /
- Health check endpoint
- Returns a simple message confirming the API is running

### POST /api/fetch_playlist
- Fetches playlist information without downloading
- Request body:
  ```json
  {
    "url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
  }
  ```

### POST /api/download_playlist
- Downloads all videos in a playlist
- Request body:
  ```json
  {
    "url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
    "output_path": "downloads"  // optional
  }
  ```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Requirements

- Python 3.7+
- FastAPI
- yt-dlp
- uvicorn

## License

MIT 