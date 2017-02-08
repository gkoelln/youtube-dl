# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    clean_html,
    compat_str,
    int_or_none,
    parse_iso8601,
    try_get,
)


class BeamProLiveIE(InfoExtractor):
    IE_NAME = 'Beam:live'
    _VALID_URL = r'https?://(?:\w+.)?beam.pro/(?P<id>[^?]+)$'
    _API_CHANNEL = 'https://beam.pro/api/v1/channels/{0}'
    _API_MANIFEST = 'https://beam.pro/api/v1/channels/{0}/manifest.m3u8'
    _RATINGS = {'family': 0, 'teen': 13, '18+': 18}

    _TEST = {
        'url': 'http://www.beam.pro/niterhayven',
        'info_dict': {
            'id': '261562',
            'ext': 'mp4',
            'uploader': 'niterhayven',
            'timestamp': 1483477281,
            'age_limit': 18,
            'title': 'Introducing The Witcher 3 //  The Grind Starts Now!',
            'thumbnail': r're:https://.*\.jpg$',
            'upload_date': '20170103',
            'uploader_id': 373396,
            'description': 'md5:0b161ac080f15fe05d18a07adb44a74d',
            'is_live': True,
        },
        'skip': 'niterhayven is offline',
        'params': {
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        channel_id = self._match_id(url)
        chan_data = self._download_json(self._API_CHANNEL.format(channel_id), channel_id)

        if not chan_data.get('online'):
            raise ExtractorError('{0} is offline'.format(channel_id), expected=True)

        formats = self._extract_m3u8_formats(
            self._API_MANIFEST.format(chan_data.get('id')), channel_id, ext='mp4')

        self._sort_formats(formats)
        info = {}
        info['formats'] = formats
        if chan_data:
            info.update(self._extract_info(chan_data))
        if not info.get('title'):
            info['title'] = self._live_title(channel_id)
        if not info.get('id'):  # barely possible but just in case
            info['id'] = compat_str(abs(hash(channel_id)) % (10 ** 8))

        return info

    def _extract_info(self, info):
        thumbnail = try_get(info, lambda x: x['thumbnail']['url'], compat_str)
        username = try_get(info, lambda x: x['user']['url'], compat_str)
        video_id = compat_str(info['id']) if info.get('id') else None
        rating = info.get('audience')

        return {
            'id': video_id,
            'title': info.get('name'),
            'description': clean_html(info.get('description')),
            'age_limit': self._RATINGS[rating] if rating in self._RATINGS else None,
            'is_live': True if info.get('online') else False,
            'timestamp': parse_iso8601(info.get('updatedAt')),
            'uploader': info.get('token') or username,
            'uploader_id': int_or_none(info.get('userId')),
            'view_count': int_or_none(info.get('viewersTotal')),
            'thumbnail': thumbnail,
        }
