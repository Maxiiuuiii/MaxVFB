================================================================================
KODI PLUGIN: Max VFB - Alle Dateien
================================================================================


================================================================================
DATEI: addon.xml
================================================================================

<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.maxvfb" name="Max VFB" version="1.0.0" provider-name="Max">
    <requires>
        <import addon="xbmc.python" version="3.0.0"/>
    </requires>
    <extension point="xbmc.python.pluginsource" library="default.py">
        <provides>video</provides>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary lang="en_GB">Max VFB Live Stream Player</summary>
        <summary lang="de_DE">Max VFB Live-Stream-Player</summary>
        <description lang="en_GB">Simple live stream player for sports events. Extracts and plays video streams from embed pages.</description>
        <description lang="de_DE">Einfacher Live-Stream-Player für Sportereignisse. Extrahiert und spielt Video-Streams von Embed-Seiten ab.</description>
        <platform>all</platform>
        <license>GPL-3.0</license>
        <website>https://github.com/yourusername/plugin.video.maxvfb</website>
        <assets>
            <icon>icon.png</icon>
            <fanart>fanart.jpg</fanart>
        </assets>
    </extension>
</addon>



================================================================================
DATEI: default.py
================================================================================

# -*- coding: utf-8 -*-
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
    """
    Extract the actual video stream URL from the embed page.
    This function fetches the embed page and looks for .m3u8 or direct video URLs.
    """
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
        m3u8_pattern = r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)'
        m3u8_urls = re.findall(m3u8_pattern, html_content)

        if m3u8_urls:
            # Return the first m3u8 URL found
            stream_url = m3u8_urls[0].replace('\\/', '/')
            xbmc.log('Max VFB: Found M3U8 URL: ' + stream_url, xbmc.LOGINFO)
            return stream_url

        # Look for .mp4 URLs
        mp4_pattern = r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)'
        mp4_urls = re.findall(mp4_pattern, html_content)

        if mp4_urls:
            stream_url = mp4_urls[0].replace('\\/', '/')
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
    """
    Returns the direct stream URL by extracting it from the embed page.
    """
    # The embed URL from the iframe
    embed_url = "https://embedsports.top/embed/alpha/torino-vs-genoa/1"

    # Extract the actual stream URL
    stream_url = extract_stream_url(embed_url)

    return stream_url

def list_streams():
    """
    Create the list of playable streams.
    """
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
    """
    Play the video stream.
    """
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
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    """
    return '{}?{}'.format(_url, urlencode(kwargs))

def router(paramstring):
    """
    Router function that calls other functions depending on the provided paramstring
    """
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



================================================================================
DATEI: README.md
================================================================================

# Max VFB - Kodi Plugin

Ein einfacher Live-Stream-Player für Kodi, der Video-Streams von Embed-Seiten extrahiert und abspielt.

## Features

- Automatische Extraktion von Stream-URLs aus Embed-Seiten
- Unterstützung für M3U8 (HLS) und MP4 Streams
- Verhindert das Öffnen externer Browser
- Einfache Bedienung

## Ordnerstruktur

```
plugin.video.maxvfb/
├── addon.xml          # Plugin-Metadaten und Konfiguration
├── default.py         # Hauptcode des Plugins
├── icon.png          # Plugin-Icon (512x512px)
├── fanart.jpg        # Hintergrundbild (1920x1080px)
├── README.md         # Diese Datei
└── .gitignore        # Git-Ignorierungsdatei
```

## Installation

### Methode 1: Lokale Installation als ZIP-Datei

1. Stelle sicher, dass alle Dateien im Ordner `plugin.video.maxvfb` sind
2. Erstelle eine ZIP-Datei mit folgendem Namen: `plugin.video.maxvfb-1.0.0.zip`
3. **Wichtig:** Die ZIP-Datei muss den Ordner `plugin.video.maxvfb` enthalten, nicht direkt die Dateien
4. In Kodi: Gehe zu **Einstellungen** → **System** → **Add-ons** → **Unbekannte Quellen** aktivieren
5. Gehe zu **Add-ons** → **Aus Zip-Datei installieren**
6. Wähle die ZIP-Datei aus
7. Warte auf die Benachrichtigung, dass das Add-on installiert wurde

### Methode 2: Installation von GitHub

1. Erstelle ein GitHub Repository (z.B. `plugin.video.maxvfb`)
2. Lade alle Dateien in das Repository hoch
3. Erstelle eine Repository-Struktur für Kodi (siehe Anleitung unten)
4. In Kodi: **Einstellungen** → **Dateimanager** → **Quelle hinzufügen**
5. Gib die URL ein: `https://raw.githubusercontent.com/DEINUSERNAME/plugin.video.maxvfb/main/`
6. Gib der Quelle einen Namen (z.B. "Max VFB Repo")
7. Gehe zu **Add-ons** → **Aus Repository installieren** → wähle dein Repository

### Methode 3: Entwicklermodus (für Tests)

1. Kopiere den Ordner `plugin.video.maxvfb` in dein Kodi Add-ons Verzeichnis:
   - **Windows:** `%APPDATA%\Kodi\addons\`
   - **Linux:** `~/.kodi/addons/`
   - **macOS:** `~/Library/Application Support/Kodi/addons/`
2. Starte Kodi neu
3. Das Plugin erscheint unter **Video-Add-ons**

## Verwendung

1. Öffne Kodi
2. Gehe zu **Add-ons** → **Video-Add-ons**
3. Klicke auf **Max VFB**
4. Wähle "Live Stream - Sports Event" aus der Liste
5. Der Stream wird automatisch gestartet

## Anpassung

Um einen anderen Stream zu verwenden:

1. Öffne `default.py` in einem Texteditor
2. Finde die Zeile: `embed_url = "https://embedsports.top/embed/alpha/torino-vs-genoa/1"`
3. Ersetze die URL mit deiner gewünschten Embed-URL
4. Speichere die Datei

Um mehrere Streams hinzuzufügen, erweitere die `list_streams()` Funktion mit zusätzlichen ListItems.

## Technische Details

### Wie funktioniert das Plugin?

1. **URL-Extraktion:** Das Plugin lädt die Embed-Seite und sucht nach direkten Video-URLs (.m3u8 oder .mp4)
2. **Pattern Matching:** Verwendet reguläre Ausdrücke um Stream-URLs im HTML-Code zu finden
3. **Direkte Wiedergabe:** Gibt die extrahierte URL direkt an Kodi's Player weiter
4. **Browser-Vermeidung:** Durch die Extraktion der direkten URL wird verhindert, dass externe Browser geöffnet werden

### Warum öffnet sich kein Browser mehr?

Das Problem entsteht normalerweise, wenn Kodi eine Embed-URL direkt öffnen soll. Diese Seiten enthalten oft JavaScript-Redirects oder Pop-ups. Unser Plugin:

- Lädt die Embed-Seite im Hintergrund
- Extrahiert die tatsächliche Video-URL
- Übergibt nur diese direkte URL an Kodi
- Kodi spielt dann direkt das Video ab, ohne die Embed-Seite zu öffnen

## Fehlerbehebung

### Das Plugin erscheint nicht in der Liste

- Stelle sicher, dass "Unbekannte Quellen" aktiviert ist
- Überprüfe, ob der Ordnername `plugin.video.maxvfb` ist
- Starte Kodi neu

### Der Stream startet nicht

- Öffne das Kodi-Log: **Einstellungen** → **System** → **Logging** → **Komponentenspezifisches Logging aktivieren**
- Suche nach Einträgen mit "Max VFB"
- Die Log-Datei zeigt, ob eine Stream-URL gefunden wurde

### "No direct stream URL found" Fehler

Dies bedeutet, dass das Plugin keine .m3u8 oder .mp4 URL auf der Embed-Seite finden konnte. Mögliche Lösungen:

- Die Embed-Seite verwendet möglicherweise verschlüsseltes oder obfuskiertes JavaScript
- Prüfe die Embed-Seite manuell im Browser und suche nach der Video-URL
- Möglicherweise muss das Pattern für die URL-Extraktion angepasst werden

## Icon und Fanart

Du musst noch folgende Dateien hinzufügen:

- **icon.png:** 512x512 Pixel, PNG-Format
- **fanart.jpg:** 1920x1080 Pixel, JPG-Format

Diese Bilder werden als Icon und Hintergrundbild für dein Plugin verwendet.

## GitHub Repository-Struktur

Um das Plugin über GitHub zu verteilen, sollte deine Repository-Struktur so aussehen:

```
repository-name/
├── plugin.video.maxvfb/
│   ├── addon.xml
│   ├── default.py
│   ├── icon.png
│   ├── fanart.jpg
│   └── README.md
├── .gitignore
└── README.md (Repository-Beschreibung)
```

## Lizenz

GPL-3.0

## Support

Bei Fragen oder Problemen:
- Erstelle ein Issue auf GitHub
- Überprüfe das Kodi-Log für detaillierte Fehlermeldungen

## Disclaimer

Dieses Plugin dient nur zu Bildungszwecken. Stelle sicher, dass du die Rechte hast, die Streams abzuspielen, auf die du zugreifst.



================================================================================
DATEI: .gitignore
================================================================================

# Python
*.pyc
*.pyo
__pycache__/
*.py[cod]

# Kodi
*.zip

# OS
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/
.idea/
*.swp
*.swo
*~


