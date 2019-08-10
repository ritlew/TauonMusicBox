# Tauon Music Box - Album chart image generator

# Copyright © 2015-2018, Taiko2k captain(dot)gxj(at)gmail.com

#     This file is part of Tauon Music Box.
#
#     Tauon Music Box is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Tauon Music Box is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Tauon Music Box.  If not, see <http://www.gnu.org/licenses/>.


import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
import cairo
from gi.repository import Pango
from gi.repository import PangoCairo
import os
from PIL import Image


class TopChart:

    def __init__(self, tauon, album_art_gen):

        self.pctl = tauon.pctl
        self.cache_dir = tauon.cache_directory
        self.user_dir = tauon.user_directory
        self.album_art_gen = album_art_gen

    def generate(self, tracks, bg=(10,10,10), rows=3, columns=3, show_lables=True, font="Monospace 10", tile=False, cascade=False):

        # Main control variables
        border = 29
        text_offset = -7
        size = 170
        spacing = 9

        mode = 1
        if cascade:
            mode = 2

        if tile:
            border = 0
            spacing = 0
            size = 160
            text_offset = 15

        # Determine the final width and height of album grid
        h = round((border * 2) + (size * rows) + (spacing * (rows - 1)))
        w = round((border * 2) + (size * columns) + (spacing * (columns - 1)))

        if mode == 2:

            r1, r2, r3 = cascade
            print(r1 * 2 + r2 * 2 + r3 * 2)
            sets = []
            for q in range(100, 10000):

                a = q / r1
                b = q / r2
                c = q / r3

                if a - int(a) == b - int(b) == c - int(c) == 0:
                    sets.append((int(a), int(b), int(c)))

            if not sets:
                return False

            abc = None
            for s in sets:
                if s[(r1, r2, r3).index(min((r1, r2, r3)))] > 165:
                    abc = s
                    break
            else:
                return False

            w = round(border * 2) + (abc[0] * r1)
            h = round(border * 2) + (abc[0] * 2) + (abc[1] * 2) + (abc[2] * 2)

        ww = w

        if show_lables:
            ww += 500  # Add extra area to final size for text

        # Prepare a blank Cairo surface
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, ww, h)
        context = cairo.Context(surface)

        bg = (bg[0] / 255, bg[1] / 255, bg[2] / 255)  # Convert 8-bit rgb values to decimal
        context.set_source_rgb(bg[0], bg[1], bg[2])
        context.paint()  # Fill in the background colour

        text = ""
        i = -1

        positions = []

        # Grid mode
        if mode == 1:
            for r in range(rows):
                for c in range(columns):

                    i += 1

                    # Break if we run out of albums
                    if i > len(tracks) - 1:
                        break

                    # Determine coordinates for current album
                    x = round(border + ((spacing + size) * c))
                    y = round(border + ((spacing + size) * r))

                    positions.append((tracks[i], x, y, size))

                positions.append(False)

        # Cascade mode
        elif mode == 2:

            a, b, c = abc

            size = a
            spacing = 0
            inv_space = 0
            if not tile:
                inv_space = 8

            x = border
            y = border
            for cl in range(r1):
                i += 1
                x = border + (spacing + size) * cl
                if i > len(tracks) - 1:
                    break
                positions.append((tracks[i], x, y, size - inv_space))
            y += spacing + size

            for cl in range(r1):
                i += 1
                x = border + (spacing + size) * cl
                if i > len(tracks) - 1:
                    break
                positions.append((tracks[i], x, y, size - inv_space))
            y += spacing + size

            size = b
            if not tile:
                inv_space = 6
            positions.append(False)

            for cl in range(r2):
                i += 1
                x = border + (spacing + size) * cl
                if i > len(tracks) - 1:
                    break
                positions.append((tracks[i], x, y, size - inv_space))
            y += spacing + size

            for cl in range(r2):
                i += 1
                x = border + (spacing + size) * cl
                if i > len(tracks) - 1:
                    break
                positions.append((tracks[i], x, y, size - inv_space))
            y += spacing + size

            size = c
            if not tile:
                inv_space = 4
            positions.append(False)

            for cl in range(r3):
                i += 1
                x = border + (spacing + size) * cl
                if i > len(tracks) - 1:
                    break
                positions.append((tracks[i], x, y, size - inv_space))
            y += spacing + size

            for cl in range(r3):
                i += 1
                x = border + (spacing + size) * cl
                if i > len(tracks) - 1:
                    break
                positions.append((tracks[i], x, y, size - inv_space))
            y += spacing + size

        for item in positions:

            if item is False:
                text += " \n"  # Insert extra line to form groups for each row
                continue

            track, x, y, size = item

            # Determine the text label line
            artist = track.artist
            if track.album_artist:
                artist = track.album_artist
            text += f"{artist} - {track.album}\n"

            # Export the album art to file object
            try:
                art_file = self.album_art_gen.save_thumb(track, (size, size), None, png=True)
            except:
                continue

            # Skip drawing this album if loading of artwork failed
            if not art_file:
                continue

            # Load image into Cairo and draw
            art = cairo.ImageSurface.create_from_png(art_file)
            context.set_source_surface(art, x, y)
            context.paint()


        if show_lables:

            # Setup font and prepare Pango layout
            options = context.get_font_options()
            options.set_antialias(cairo.ANTIALIAS_GRAY)
            context.set_font_options(options)
            layout = PangoCairo.create_layout(context)
            layout.set_ellipsize(Pango.EllipsizeMode.END)
            layout.set_width((500 - text_offset - spacing) * 1000)
            # layout.set_height((h - spacing * 2) * 1000)
            #layout.set_spacing(3 * 1000)
            layout.set_font_description(Pango.FontDescription(font))
            layout.set_text(text, -1)

            # Here we make sure the font size is small enough to fit
            font_comp = font.split(" ")
            font_size = font_comp.pop()
            try:
                font_size = int(font_size)
                while font_size > 2:
                    th = layout.get_pixel_size()[1]
                    if th < h - border:
                        break
                    font_size -= 1
                    font = " ".join(font_comp) + " " + str(font_size)
                    layout.set_font_description(Pango.FontDescription(font))
                    layout.set_text(text, -1)
            except:
                print("error adjusting font size")

            # All good to render now
            y_text_padding = 3
            if tile:
                y_text_padding += 6
            context.translate(w + text_offset, border + y_text_padding)
            context.set_source_rgb(0.9, 0.9, 0.9)
            PangoCairo.show_layout(context, layout)

        # Finally export as PNG
        output_path = os.path.join(self.user_dir, "chart.png")
        surface.write_to_png(output_path)

        # Convert to JPEG for convenience
        output_path2 = os.path.join(self.user_dir, "chart.jpg")
        im = Image.open(output_path)
        im.save(output_path2, 'JPEG', quality=92)

        return output_path2
