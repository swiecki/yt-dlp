from .common import InfoExtractor
from ..utils import smuggle_url
import json
import re
import isodate

class CNBCIE(InfoExtractor):
    _VALID_URL = r"https?://video\.cnbc\.com/gallery/\?video=(?P<id>[0-9]+)"
    _TEST = {
        "url": "http://video.cnbc.com/gallery/?video=3000503714",
        "info_dict": {
            "id": "3000503714",
            "ext": "mp4",
            "title": "Fighting zombies is big business",
            "description": "md5:0c100d8e1a7947bd2feec9a5550e519e",
            "timestamp": 1459332000,
            "upload_date": "20160330",
            "uploader": "NBCU-CNBC",
        },
        "params": {
            # m3u8 download
            "skip_download": True,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        return {
            "_type": "url_transparent",
            "ie_key": "ThePlatform",
            "url": smuggle_url(
                "http://link.theplatform.com/s/gZWlPC/media/guid/2408950221/%s?mbr=true&manifest=m3u"
                % video_id,
                {"force_smil_url": True},
            ),
            "id": video_id,
        }


class CNBCVideoIE(InfoExtractor):
    _VALID_URL = r"https?://(?:www\.)?cnbc\.com(?P<path>/video/(?:[^/]+/)+(?P<id>[^./?#&]+)\.html)"
    _TEST = {
        "url": "https://www.cnbc.com/video/2018/07/19/trump-i-dont-necessarily-agree-with-raising-rates.html",
        "info_dict": {
            "id": "7000031301",
            "ext": "mp4",
            "title": "Trump: I don't necessarily agree with raising rates",
            "description": "md5:878d8f0b4ebb5bb1dda3514b91b49de3",
            "timestamp": 1531958400,
            "upload_date": "20180719",
            "uploader": "NBCU-CNBC",
        },
        "params": {
            "skip_download": True,
        },
    }

    def _real_extract(self, url):
        name = self._match_id(url)
        webpage = self._download_webpage(url, name)

        json_data = self._search_regex(
            (r'<script type="application\/ld\+json">(.*?)<\/script>',),
            webpage,
            "json",
            default=None,
            flags=re.DOTALL,  # This makes '.' match also newline characters
        )
        data = json.loads(json_data)

        description=data.get("description",None)
        title = data.get("name", None)
        upload_date = data.get("uploadDate", None)


        #duration
        duration = None
        if data.get("duration", None):
            duration_str = data.get("duration")  # your ISO 8601 duration string
            duration = isodate.parse_duration(duration_str)
            duration = duration.total_seconds()
            
        video_data = self._search_regex(
            (r'encodings":(\[.*?\])'), webpage, "encodings", default=None
        )

        if not video_data:
            return
        embeddings = json.loads(video_data)
        toReturn = {
            "id": name,
            "title": name,
            "description": description,
            "duration": duration,
            "upload_date": upload_date,
            "formats": self._extract_m3u8_formats(
                embeddings[0]["url"], name, "mp4", m3u8_id="hls", fatal=False
            ),
        }
        return toReturn
