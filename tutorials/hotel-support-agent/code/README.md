# Sanctuary Hotel website prototype

The saved hotel design, with its original AI-generated images, carousel, guest
guide, and scripted concierge interactions. No model, database, calendar, booking,
or message-sending service is connected. Requests exist only in the page until
it is reset or reloaded. The sample stay and activity dates are fixed demo data.

## Install

Use Python 3 and Node.js (Node is needed only for the syntax check). There are no
application packages to install and no build step.

## Run

From `tutorials/hotel-support-agent/code`:

```bash
python3 -m http.server 8773 --bind 127.0.0.1 --directory website
```

Open http://127.0.0.1:8773/. Expect the forest-pool hero and the Sanctuary Hotel name.
If the port is occupied, stop your earlier preview or choose another local port.
Do not expose Python's development server as a production service.

Google Fonts supplies Jost and Cormorant Garamond. Without internet access the
site uses fallback fonts. All photographs, the hero video, JavaScript, and CSS are local.

## Test

From `tutorials/hotel-support-agent/code`:

```bash
python3 verify_website.py
node --check website/app.js
```

The first command checks HTML asset paths, section links, and carousel images.
The second checks JavaScript syntax. Neither calls a model or needs credentials.

In a browser, advance and reverse the villa carousel, open the navigation, ask
about breakfast, ask about tomorrow, and prepare a request. The request must say
nothing has been sent or booked. Click New conversation to return to the welcome
screen. Check the browser console for errors and confirm all images load.

## Reset

Click **New conversation**, or reload the page. There is no database or browser
storage to clear. Stop the local server with Ctrl-C.

## Image provenance

`website/assets/forest-pool.png`, `suite.png`, and `breakfast.png` were generated
for the fictional Sanctuary Hotel concept during the design exploration. They are
illustrations, not photographs of an actual property. No reference-site image is
required at runtime. Preserve the demo notices when reusing this prototype.

The active `website/assets/hero-rotation.mp4` hero is an 18-second silent loop
of three AI-generated stills: the original pool, a daylight bedroom, and the
restaurant at dusk. Each scene holds for four seconds with two-second
crossfades, including the return to the pool. There is no camera movement.
The earlier Seedance clip remains in `forest-pool.mp4` for reference.
Playback loops without visible controls; reduced-motion visitors see the
original pool still. If playback fails, the still remains visible.

## Connecting the real agent

Keep this layout and replace the scripted `ask()` response selection with a
server API call. Session ownership, tool execution, confirmation enforcement,
and persistence belong in the backend. Do not put model or calendar credentials
in `website/app.js`. See the [lesson](../LESSON.md) for the proposed system and
[setup guide](../resources/setup-guide.md) for the development tools.
