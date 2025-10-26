
# Now let's create an improved version that includes functionality to extract the actual stream URL
# We'll create all the necessary files for the Kodi plugin

# Advanced default.py with stream extraction
advanced_default_py = """# -*- coding: utf-8 -*-
import sys
import re
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
try:
    from urllib.parse import urlencode, parse_qsl
    import urllib.request as urllib_request
except ImportError:
    from urlparse import parse_qsl
    from urllib import urlencode
    import urllib2 as urllib_request

# Get addon handle and instance
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()

def extract_stream_url(embed_url):
    \"\"\"
    Extract the actual video stream URL from the embed page.
    This function fetches the embed page and looks for .m3u8 or direct video URLs.
    \"\"\"
    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': embed_url
        }
        
        # Create request with headers
        req = urllib_request.Request(embed_url, headers=headers)
        response = urllib_request.urlopen(req)
        html_content = response.read().decode('utf-8')
        
        # Look for .m3u8 URLs (HLS streams)
        m3u8_pattern = r'(https?://[^\\s\"\\'<>]+\\.m3u8[^\\s\"\\'<>]*)'
        m3u8_urls = re.findall(m3u8_pattern, html_content)
        
        if m3u8_urls:
            # Return the first m3u8 URL found
            stream_url = m3u8_urls[0].replace('\\\\/', '/')
            xbmc.log('Max VFB: Found M3U8 URL: ' + stream_url, xbmc.LOGINFO)
            return stream_url
        
        # Look for .mp4 URLs
        mp4_pattern = r'(https?://[^\\s\"\\'<>]+\\.mp4[^\\s\"\\'<>]*)'
        mp4_urls = re.findall(mp4_pattern, html_content)
        
        if mp4_urls:
            stream_url = mp4_urls[0].replace('\\\\/', '/')
            xbmc.log('Max VFB: Found MP4 URL: ' + stream_url, xbmc.LOGINFO)
            return stream_url
            
        # If no direct URL found, return the embed URL
        # Kodi will try to handle it with its internal browser
        xbmc.log('Max VFB: No direct stream URL found, using embed URL', xbmc.LOGWARNING)
        return embed_url
        
    except Exception as e:
        xbmc.log('Max VFB: Error extracting stream URL: ' + str(e), xbmc.LOGERROR)
        # Return embed URL as fallback
        return embed_url

def get_stream_url():
    \"\"\"
    Returns the direct stream URL by extracting it from the embed page.
    \"\"\"
    # The embed URL from the iframe
    embed_url = "https://embedsports.top/embed/alpha/torino-vs-genoa/1"
    
    # Extract the actual stream URL
    stream_url = extract_stream_url(embed_url)
    
    return stream_url

def list_streams():
    \"\"\"
    Create the list of playable streams.
    \"\"\"
    xbmcplugin.setPluginCategory(_handle, 'Max VFB Streams')
    xbmcplugin.setContent(_handle, 'videos')
    
    # Create a list item for the stream
    list_item = xbmcgui.ListItem(label='Live Stream - Sports Event')
    
    # Set the graphics (thumbnail, fanart)
    list_item.setArt({
        'thumb': _addon.getAddonInfo('icon'),
        'icon': _addon.getAddonInfo('icon'),
        'fanart': _addon.getAddonInfo('fanart')
    })
    
    # Set additional info for the list item
    list_item.setInfo('video', {
        'title': 'Live Stream',
        'genre': 'Sports',
        'mediatype': 'video',
        'plot': 'Live sports stream from embedsports'
    })
    
    # Set the item as playable
    list_item.setProperty('IsPlayable', 'true')
    
    # Create URL for playing
    url = get_url(action='play', video='stream1')
    
    # Add the item to the list
    is_folder = False
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
    # Finish creating the directory
    xbmcplugin.endOfDirectory(_handle)

def play_stream():
    \"\"\"
    Play the video stream.
    \"\"\"
    # Get the stream URL
    stream_url = get_stream_url()
    
    # Create a playable item
    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setProperty('IsPlayable', 'true')
    
    # Set video stream info for better playback
    play_item.setInfo('video', {
        'title': 'Live Stream',
        'mediatype': 'video'
    })
    
    # Important: Set mimetype for HLS streams
    if '.m3u8' in stream_url:
        play_item.setMimeType('application/vnd.apple.mpegurl')
        play_item.setContentLookup(False)
    
    # Pass the item to the Kodi player for playback
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def get_url(**kwargs):
    \"\"\"
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    \"\"\"
    return '{}?{}'.format(_url, urlencode(kwargs))

def router(paramstring):
    \"\"\"
    Router function that calls other functions depending on the provided paramstring
    \"\"\"
    # Parse a URL-encoded paramstring to the dictionary of {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    
    # Check the parameters passed to the plugin
    if params:
        if params.get('action') == 'play':
            # Play the stream
            play_stream()
        else:
            # If the provided paramstring does not contain a supported action
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of streams
        list_streams()

if __name__ == '__main__':
    # Get the plugin url in plugin:// notation
    _url = sys.argv[0]
    # Call the router function and pass the plugin call parameters to it
    router(sys.argv[2][1:])
"""

print("=== Erweiterte Version erstellt ===\n")
print("Diese Version enthält:")
print("1. Automatische Extraktion der Stream-URL aus der Embed-Seite")
print("2. Unterstützung für .m3u8 (HLS) und .mp4 Streams")
print("3. Proper Headers um als Browser erkannt zu werden")
print("4. Error-Handling und Logging")
print("5. Verhindert das Öffnen externer Browser durch direkte URL-Extraktion")
print("\nDie Funktion extract_stream_url() parst die Embed-Seite und")
print("sucht nach direkten Video-URLs, sodass Kodi das Video direkt")
print("abspielen kann ohne externe Websites zu öffnen.")

# Now let's create an improved version that includes functionality to extract the actual stream URL
# We'll create all the necessary files for the Kodi plugin

# Advanced default.py with stream extraction
advanced_default_py = """# -*- coding: utf-8 -*-
import sys
import re
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
try:
    from urllib.parse import urlencode, parse_qsl
    import urllib.request as urllib_request
except ImportError:
    from urlparse import parse_qsl
    from urllib import urlencode
    import urllib2 as urllib_request

# Get addon handle and instance
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()

def extract_stream_url(embed_url):
    \"\"\"
    Extract the actual video stream URL from the embed page.
    This function fetches the embed page and looks for .m3u8 or direct video URLs.
    \"\"\"
    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': embed_url
        }
        
        # Create request with headers
        req = urllib_request.Request(embed_url, headers=headers)
        response = urllib_request.urlopen(req)
        html_content = response.read().decode('utf-8')
        
        # Look for .m3u8 URLs (HLS streams)
        m3u8_pattern = r'(https?://[^\\s\"\\'<>]+\\.m3u8[^\\s\"\\'<>]*)'
        m3u8_urls = re.findall(m3u8_pattern, html_content)
        
        if m3u8_urls:
            # Return the first m3u8 URL found
            stream_url = m3u8_urls[0].replace('\\\\/', '/')
            xbmc.log('Max VFB: Found M3U8 URL: ' + stream_url, xbmc.LOGINFO)
            return stream_url
        
        # Look for .mp4 URLs
        mp4_pattern = r'(https?://[^\\s\"\\'<>]+\\.mp4[^\\s\"\\'<>]*)'
        mp4_urls = re.findall(mp4_pattern, html_content)
        
        if mp4_urls:
            stream_url = mp4_urls[0].replace('\\\\/', '/')
            xbmc.log('Max VFB: Found MP4 URL: ' + stream_url, xbmc.LOGINFO)
            return stream_url
            
        # If no direct URL found, return the embed URL
        # Kodi will try to handle it with its internal browser
        xbmc.log('Max VFB: No direct stream URL found, using embed URL', xbmc.LOGWARNING)
        return embed_url
        
    except Exception as e:
        xbmc.log('Max VFB: Error extracting stream URL: ' + str(e), xbmc.LOGERROR)
        # Return embed URL as fallback
        return embed_url

def get_stream_url():
    \"\"\"
    Returns the direct stream URL by extracting it from the embed page.
    \"\"\"
    # The embed URL from the iframe
    embed_url = "https://embedsports.top/embed/alpha/torino-vs-genoa/1"
    
    # Extract the actual stream URL
    stream_url = extract_stream_url(embed_url)
    
    return stream_url

def list_streams():
    \"\"\"
    Create the list of playable streams.
    \"\"\"
    xbmcplugin.setPluginCategory(_handle, 'Max VFB Streams')
    xbmcplugin.setContent(_handle, 'videos')
    
    # Create a list item for the stream
    list_item = xbmcgui.ListItem(label='Live Stream - Sports Event')
    
    # Set the graphics (thumbnail, fanart)
    list_item.setArt({
        'thumb': _addon.getAddonInfo('icon'),
        'icon': _addon.getAddonInfo('icon'),
        'fanart': _addon.getAddonInfo('fanart')
    })
    
    # Set additional info for the list item
    list_item.setInfo('video', {
        'title': 'Live Stream',
        'genre': 'Sports',
        'mediatype': 'video',
        'plot': 'Live sports stream from embedsports'
    })
    
    # Set the item as playable
    list_item.setProperty('IsPlayable', 'true')
    
    # Create URL for playing
    url = get_url(action='play', video='stream1')
    
    # Add the item to the list
    is_folder = False
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
    # Finish creating the directory
    xbmcplugin.endOfDirectory(_handle)

def play_stream():
    \"\"\"
    Play the video stream.
    \"\"\"
    # Get the stream URL
    stream_url = get_stream_url()
    
    # Create a playable item
    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setProperty('IsPlayable', 'true')
    
    # Set video stream info for better playback
    play_item.setInfo('video', {
        'title': 'Live Stream',
        'mediatype': 'video'
    })
    
    # Important: Set mimetype for HLS streams
    if '.m3u8' in stream_url:
        play_item.setMimeType('application/vnd.apple.mpegurl')
        play_item.setContentLookup(False)
    
    # Pass the item to the Kodi player for playback
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def get_url(**kwargs):
    \"\"\"
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    \"\"\"
    return '{}?{}'.format(_url, urlencode(kwargs))

def router(paramstring):
    \"\"\"
    Router function that calls other functions depending on the provided paramstring
    \"\"\"
    # Parse a URL-encoded paramstring to the dictionary of {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    
    # Check the parameters passed to the plugin
    if params:
        if params.get('action') == 'play':
            # Play the stream
            play_stream()
        else:
            # If the provided paramstring does not contain a supported action
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of streams
        list_streams()

if __name__ == '__main__':
    # Get the plugin url in plugin:// notation
    _url = sys.argv[0]
    # Call the router function and pass the plugin call parameters to it
    router(sys.argv[2][1:])
"""

print("=== Erweiterte Version erstellt ===\n")
print("Diese Version enthält:")
print("1. Automatische Extraktion der Stream-URL aus der Embed-Seite")
print("2. Unterstützung für .m3u8 (HLS) und .mp4 Streams")
print("3. Proper Headers um als Browser erkannt zu werden")
print("4. Error-Handling und Logging")
print("5. Verhindert das Öffnen externer Browser durch direkte URL-Extraktion")
print("\nDie Funktion extract_stream_url() parst die Embed-Seite und")
print("sucht nach direkten Video-URLs, sodass Kodi das Video direkt")
print("abspielen kann ohne externe Websites zu öffnen.")
