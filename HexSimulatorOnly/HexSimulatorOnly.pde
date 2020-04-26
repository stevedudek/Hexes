/*
  Hex Simulator Only - draws hexes on the monitor
  
  Stripped down simulator to use with the DMX king
  
  No logic: all received (pixel, color) messages are drawn immediately
  
  Colors are hsv, because that's what the Python Showrunner uses
  
  Compatible with Processing 2 + 3
  
  4/21/20
  
*/

// Number of Big Hexes (make sure this agrees with the one in hex.py)
final int NUM_HEXES = 2;   

// Wiring diagram - needs to be the same for all fabricated Hexes
// (that's all - just a lookup table matching coordinate to LED)
int[][] LED_LOOKUP = {
  { -1, -1, -1, -1, -1, 55, 59, 60, 94, 93,  98},
  { -1, -1, -1, -1, 54, 53, 61, 62, 92, 91,  99},
  { -1, -1, -1, 16, 52, 51, 63, 64, 90, 89, 101},
  { -1, -1, 17, 18, 50, 49, 65, 66, 88, 87, 102},
  { -1, 12, 19, 20, 48, 47, 67, 68, 86, 85, 104},
  { 11, 10, 21, 22, 46, 45, 69, 70, 84, 83, 105},
  {  9,  8, 23, 24, 44, 43, 71, 72, 82, 81,  -1},
  {  7,  6, 25, 26, 42, 41, 73, 74, 80, -1,  -1},
  {  5,  4, 27, 28, 40, 39, 75, 76, -1, -1,  -1},
  {  3,  2, 29, 30, 38, 37, 77, -1, -1, -1,  -1},
  {  1,  0, 31, 32, 36, 35, -1, -1, -1, -1,  -1}
};

//
//  Hex shape primitives
//
int HEX_SIZE = 20;

public float hexWidth() {
  return 0.75 * hexHeight();
}
  
public float hexHeight() {
  return HEX_SIZE * 2;    
}
  
public float vertDistance() {
  return sqrt(3)/2 * hexHeight();
}

import processing.net.*;
import java.util.*;
import java.util.regex.*;
import java.awt.Color;

// network vars
int port = 4444;
Server _server; 
StringBuffer _buf;

// How many little hexes on the base of each big hex
int PIXEL_WIDTH = 11;  // Height & width in pixels (LEDs) of each hex
int HEX_OFFSET = 5;  // Offset to add to hex coordinate to make all coordinates positive
int NUM_PIXELS = PIXEL_WIDTH * PIXEL_WIDTH;
int NUM_LEDS = 106;  // includes spacer leds

// Calculated pixel constants for simulator display
int SCREEN_SIZE = 1200;  // hex screenfloat SMALL_SIZE = (SCREEN_SIZE - 20) / (PIXEL_WIDTH * NUM_HEXES);  // Size of a small hex
int BIG_HEX_WIDTH = (int)(hexHeight() * PIXEL_WIDTH);  // Width of one big hex
int SCREEN_WIDTH = (int)((BIG_HEX_WIDTH) * NUM_HEXES);
int SCREEN_HEIGHT = (int)(vertDistance() * PIXEL_WIDTH) + 20; // Height + a little
int DRAW_LABELS = 2;

HexForm[] bigHex = new HexForm[NUM_HEXES];  // Grid model of Big Hexes

//
// Helper classes: Coord
//
class Coord {
  public int x, y;
  
  Coord(int x, int y) {
    this.x = x;
    this.y = y;
  }
}

//
// setup
//
void settings() {
  size(SCREEN_WIDTH, SCREEN_HEIGHT);  // Processing 3
}

void setup() {
  size(SCREEN_WIDTH, SCREEN_HEIGHT);  // Processing 2 (comment out if using 3)
  colorMode(HSB, 255);  // HSB colors (not hsv)
  
  stroke(0);
  fill(0, 0, 128);
  
  frameRate(10);
  
  for (int h = 0; h < NUM_HEXES; h++) {
    bigHex[h] = makeBigHex(h);
  }
  
  _buf = new StringBuffer();
  _server = new Server(this, port);
  println("server listening: " + _server);
  
  drawHexes();
}

void draw() {
  // Get (pixel, color) messages from python show runner
  // and draw them as fast as possible
  pollServer();  
}

void drawHexes() {
  for (int h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          bigHex[h].hexes[x][y].draw();
        }
      }
    }
  }
}

//
// Converts an x,y hex coordinate into a (strip, LED) light coordinate
//
int GetLightFromCoord(int x, int y) {
  if (x < 0 || y < 0) {
    println("Illegal hex coordinate: %d,%d", x, y);
    return 0;
  }
  return LED_LOOKUP[x][y];  // These must be positive!
}

//
// HexForm class holds an 2D-array of Hexes (another class) 
//
HexForm makeBigHex(int h) {
  HexForm form = new HexForm(h, PIXEL_WIDTH, PIXEL_WIDTH);
  
  for (int x = 0; x < PIXEL_WIDTH; x++) {
     for (int y = 0; y < PIXEL_WIDTH; y++) {
       form.add(new Hex(h, x, y), x, y);
     }
  }
  return form;
}

class HexForm {
  Hex[][] hexes;
  int hex_number;
  int x_width;
  int y_height;
  
  HexForm(int hex_number, int x_width, int y_height) {
    this.hexes = new Hex[x_width][y_height];
    this.hex_number = hex_number;
    this.x_width = x_width;
    this.y_height = y_height;
  }
  
  boolean InBounds(int x, int y) {
    return (x >= 0 && x < this.x_width && y >= 0 && y < this.y_height);
  }
  
  void add(Hex hex, int x, int y) {
    if (InBounds(x, y)) {
      this.hexes[x][y] = hex;
    }
  }
  
  int getLED(byte x, byte y) {
    return this.hexes[x][y].LED;
  }
  
  void draw() {
    for (byte x = 0; x < this.x_width; x++) {
      for (byte y = 0; y < this.y_height; y++) {
        if (hexExists(x,y)) {
          this.hexes[x][y].draw();
        }
      }
    }
  }
  
  void setCellColor(int c, byte x, byte y) {
    if (InBounds(x, y)) { 
      this.hexes[x][y].setColor(c);
    }
  }
  
  boolean hexExists(byte x, byte y) {
    return (InBounds(x, y) && this.hexes[x][y] != null && this.hexes[x][y].exists);
  }
}

//
//  Hex shape primitives
//
class Hex {
  String id = null; // "xcoord, ycoord"
  int x;  // x in the hex array
  int y;  // y in the hex array
  float pix_x;  // screen x-coordinate
  float pix_y;  // screen y-coordinate
  int strip;  // strip number
  int LED;  // LED number on the strand
  int c;  // color
  boolean exists;  // Is the hex on the grid?
  
  Hex(int i, int x, int y) {
    this.strip = i;
    this.x = x;
    this.y = y;
    Coord pixel = calculate_coord(i, y, x);
    this.pix_x = pixel.x;
    this.pix_y = pixel.y;
    this.LED = GetLightFromCoord(x, y);
    this.c = get_hsv_color(0, 0, 255);
    this.exists = (this.LED != -1);
    
    int[] coords = new int[2];
    coords[1] = x - HEX_OFFSET;
    coords[0] = y - HEX_OFFSET;
    this.id = join(nf(coords, 0), ",");
  }
  
  void setColor(int c) {
    this.c = c;
  }
  
  Coord calculate_coord(int i, int x, int y) {
    // Calculate the pixel coordinate on hex i at position x,y
    int y_offset = int(y/2);
    int pixel_x = int(get_bighex_x(i) + ((x + y_offset) * vertDistance()) + ((y % 2) * 0.5 * vertDistance()));
    int pixel_y = int((y + 1.5) * hexWidth());
    
    return new Coord(pixel_x, pixel_y);
  }
  
  int get_bighex_x(int i) {
    return (BIG_HEX_WIDTH * i) - int(vertDistance());
  }
  
  void draw() {
    // Draw the hexagon and fill it with color
    fill(get_hue(this.c), get_sat(this.c), get_val(this.c));
    stroke(0);
    
    // This is hugely expensive
    beginShape();
    for (int i = 0; i < 6; i++) {
      float angle = (2 * PI) / 6 * (i + 0.5);
      int x_coord = int(this.pix_x + HEX_SIZE * cos(angle));
      int y_coord = int(this.pix_y + HEX_SIZE * sin(angle));
      vertex(x_coord, y_coord);
    }
    endShape(CLOSE);
    
    // toggle text label between light number and x,y coordinate
    String text = "";
    int[] coords = new int[2];
    switch (DRAW_LABELS) {
      case 0:
        text = this.id;
        break;
      case 1:
        coords[0] = this.strip;
        coords[1] = this.LED;
        text = join(nf(coords, 0), ",");
        break;
      case 2:
        break;  // no label
    }
    
    if (text != "" && this.id != null) {
      fill(0);
      textAlign(CENTER);
      text(text, this.pix_x, this.pix_y);
    }
    noFill();
  }
}

//
//  Server Routines
//
void pollServer() {
  try {
    Client c = _server.available();
    // append any available bytes to the buffer
    if (c != null) {
      _buf.append(c.readString());
    }
    // process as many lines as we can find in the buffer
    int ix = _buf.indexOf("\n");
    while (ix > -1) {
      String msg = _buf.substring(0, ix);
      msg = msg.trim();
      processCommand(msg);
      _buf.delete(0, ix+1);
      ix = _buf.indexOf("\n");
    }
  } catch (Exception e) {
    println("exception handling network command");
    e.printStackTrace();
  }
}

//
// processCommand - process 6 integers as (h, x, y, int hsv)
// x and y are +5 offset, so to be always positive

// 4 comma-separated numbers for i, x, y, color
//
Pattern cmd_pattern = Pattern.compile("^\\s*(\\d+),(\\d+),(\\d+),(\\d+)\\s*$");

void processCommand(String cmd) {
  if (cmd.length() < 2) { return; }  // Discard erroneous stub characters
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    //println(cmd);
    println("ignoring input for " + cmd);
    return;
  }
  byte h  =    Byte.valueOf(m.group(1));
  byte x  =    Byte.valueOf(m.group(2));  // 0+ (do the offset just before sending)
  byte y  =    Byte.valueOf(m.group(3));  // 0+ (do the offset just before sending)
  int hsv = Integer.valueOf(m.group(4));
  
  if (bigHex[h].hexExists(x,y)) {
    bigHex[h].hexes[x][y].setColor(hsv);
    bigHex[h].hexes[x][y].draw();
  }
          
//  println(String.format("setting hex %d coord:%d,%d to h:%d, s:%d, v:%d", h, x, y, get_hue(hsv), get_sat(hsv), get_val(hsv)));
}


int get_hsv_color(int h, int s, int v) {
  return h << 16 | s << 8 | v;
}

short get_hue(int c) {
  return (short)(c >> 16 & 0xFF);
}

short get_sat(int c) {
  return (short)(c >> 8 & 0xFF);
}

short get_val(int c) {
  return (short)(c & 0xFF);
}

void print_memory_usage() {
  long maxMemory = Runtime.getRuntime().maxMemory();
  long allocatedMemory = Runtime.getRuntime().totalMemory();
  long freeMemory = Runtime.getRuntime().freeMemory();
  int inUseMb = int(allocatedMemory / 1000000);
  
  if (inUseMb > 80) {
    println("Memory in use: " + inUseMb + "Mb");
  }  
}
