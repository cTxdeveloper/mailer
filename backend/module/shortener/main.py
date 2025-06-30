# updates(v1.0)
# this api is not yet finished and is expected to be finished on (v2.1)
# this is a place holder, for the url shortner api, we may have it on a domain like txtxtxt.co (to avoid gmail/ and etc blocking)
import json, os, uuid, hashlib

from datetime import datetime, timezone
from typing import Optional, List

# fast api [v-xxx-xxxx]
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

# rate limit lib  (v1.0)
from slowapi import Limiter 
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

with open(
     "config.json",
     "r"
) as f:
     config = json.load(f)

app = FastAPI()
templates = Jinja2Templates(
     directory="templates"
)
app.mount(
     "/static",
     StaticFiles(
          directory="static"
     ),
     name="static"
)

limiter = Limiter(
     key_func=get_remote_address
)
app.state.limiter = limiter

def verify_api_key(request: Request, call_next):
     protected = request.url.path.startswith(
          "/shorten"
     ) or request.url.path.startswith(
          "/admin"
     )
     if protected:
          key = request.headers.get(
               "X-API-Key"
          )
          if key not in config["url_shortener"].get(
               "api_keys",
               []
          ):
               raise HTTPException(
                    status_code=401,
                    detail="Unauthorized"
               )
     return call_next(
          request
     )

app.middleware(
     "http"
)(verify_api_key)

async def rate_limit_handler(request, exc):
     return PlainTextResponse(
          "Rate limit exceeded",
          status_code=429
     )

app.exception_handler(
     RateLimitExceeded
)(rate_limit_handler)

url_map = {}
file_path = config["url_shortener"]["storage"]["file_path"]
if os.path.exists(
     file_path
):
     with open(
          file_path,
          "r"
     ) as f:
          url_map = json.load(
               f
          )

class ShortenRequest(BaseModel):
     url: HttpUrl
     expires_at: Optional[str] = None
     max_clicks: Optional[int] = None
     tags: Optional[List[str]] = []

class ShortenResponse(BaseModel):
     short_url: str

@limiter.limit("30/minute")
@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(
     request_data: ShortenRequest
):
     while True:
          raw = f"{request_data.url}{uuid.uuid4()}"
          code = hashlib.sha256(
               raw.encode()
          ).hexdigest()[:6]
          if code not in url_map:
               break

     url_map[code] = {
          "url": str(
               request_data.url
          ),
          "created_at": datetime.now(
               timezone.utc
          ).isoformat(),
          "expires_at": request_data.expires_at,
          "max_clicks": request_data.max_clicks,
          "clicks": [],
          "tags": request_data.tags
     }

     with open(
          file_path,
          "w"
     ) as f:
          json.dump(
               url_map,
               f,
               indent=4
          )

     return ShortenResponse(
          short_url=f"{config['url_shortener']['domain'].rstrip('/')}/{code}"
     )

@app.get("/{short_code}")
def redirect_to_url(
     short_code: str,
     request: Request
):
     if short_code not in url_map:
          raise HTTPException(
               status_code=404,
               detail="Short URL not found"
          )

     entry = url_map[short_code]

     if entry.get("expires_at"):
          expires = datetime.fromisoformat(
               entry["expires_at"]
          )
          if datetime.now(
               timezone.utc
          ) > expires:
               raise HTTPException(
                    status_code=410,
                    detail="Link has expired"
               )

     if entry.get("max_clicks") is not None:
          if len(
               entry["clicks"]
          ) >= entry["max_clicks"]:
               raise HTTPException(
                    status_code=410,
                    detail="Click limit reached"
               )

     entry["clicks"].append({
          "timestamp": datetime.now(
               timezone.utc
          ).isoformat(),
          "ip": request.client.host,
          "user_agent": request.headers.get(
               "user-agent",
               "unknown"
          )
     })

     with open(
          file_path,
          "w"
     ) as f:
          json.dump(
               url_map,
               f,
               indent=4
          )

     return RedirectResponse(
          url=entry["url"]
     )

@app.get("/admin/links")
def list_links():
     return url_map

@app.get("/admin/links/{short_code}")
def get_link_info(
     short_code: str
):
     if short_code not in url_map:
          raise HTTPException(
               status_code=404,
               detail="Link not found"
          )
     return url_map[short_code]

@app.delete("/admin/links/{short_code}")
def delete_link(
     short_code: str
):
     if short_code not in url_map:
          raise HTTPException(
               status_code=404,
               detail="Link not found"
          )
     del url_map[short_code]
     with open(
          file_path,
          "w"
     ) as f:
          json.dump(
               url_map,
               f,
               indent=4
          )
     return {
          "detail": f"Short link '{short_code}' deleted"
     }

@app.get("/admin/search")
def search_links(
     tag: str = None,
     domain: str = None
):
     results = {}
     for code, data in url_map.items():
          if tag and tag not in data.get("tags", []):
               continue
          if domain and domain not in data["url"]:
               continue
          results[code] = data
     return results

@app.get("/admin/export")
def export_links():
     backup_path = "database/backup/urls-backup.json"
     os.makedirs(
          os.path.dirname(
               backup_path
          ),
          exist_ok=True
     )
     with open(
          backup_path,
          "w"
     ) as f:
          json.dump(
               url_map,
               f,
               indent=4
          )
     return {
          "status": "success",
          "backup_file": backup_path
     }

@app.get("/admin/dashboard")
def dashboard(
     request: Request
):
     return templates.TemplateResponse(
          "dashboard.html",
          {
               "request": request,
               "url_map": url_map
          }
     )