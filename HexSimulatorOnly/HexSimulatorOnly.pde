/*
  Hex Simulator Only
  
  1. Simulator: draws hexes on the monitor
  
  Stripped down simulator to use with the DMX king
  
  4/21/20
  
*/

int NUM_HEXES = 2;  // Number of Big Hexes

// Wiring diagram - needs to be the same for all fabricated Hexes
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

int[] DIM_AMOUNT = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 
   1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 
   8, 8, 9, 9, 9, 10, 10, 11, 11, 12, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 
   17, 18, 18, 19, 19, 20, 21, 21, 22, 22, 23, 24, 24, 25, 25, 26, 27, 27, 28, 29, 
   29, 30, 31, 31, 32, 33, 34, 34, 35, 36, 37, 37, 38, 39, 40, 41, 41, 42, 43, 44, 
   45, 45, 46, 47, 48, 49, 50, 51, 52, 53, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 
   63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 82, 83, 
   84, 86, 87, 88, 89, 90, 92, 93, 94, 95, 96, 98, 99, 100, 101, 103, 104, 105, 106, 
   108, 109, 110, 112, 113, 114, 116, 117, 118, 120, 121, 123, 124, 125, 127, 128, 
   130, 131, 132, 134, 135, 137, 138, 140, 141, 143, 144, 146, 147, 149, 150, 152, 
   153, 155, 157, 158, 160, 161, 163, 164, 166, 168, 169, 171, 173, 174, 176, 178, 
   179, 181, 183, 184, 186, 188, 189, 191, 193, 195, 196, 198, 200, 202, 203, 205, 
   207, 209, 211, 212, 214, 216, 218, 220, 222, 224, 225, 227, 229, 231, 233, 235, 
   237, 239, 241, 243, 245, 247, 249, 251, 253, 255 };

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

// Color buffers: [x][y][r,g,b]
// Two buffers permits updating only the lights that change color
// May improve performance and reduce flickering
int[][][] curr_buffer = new int[NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];
int[][][] next_buffer = new int[NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];

// Calculated pixel constants for simulator display
int SCREEN_SIZE = 1200;  // hex screenfloat SMALL_SIZE = (SCREEN_SIZE - 20) / (PIXEL_WIDTH * NUM_HEXES);  // Size of a small hex
int BIG_HEX_WIDTH = (int)(hexHeight() * PIXEL_WIDTH);  // Width of one big hex
int SCREEN_WIDTH = (int)((BIG_HEX_WIDTH) * NUM_HEXES);
int SCREEN_HEIGHT = (int)(vertDistance() * PIXEL_WIDTH) + 20; // Height + a little
int DRAW_LABELS = 0;

HexForm[] bigHex = new HexForm[NUM_HEXES];  // Grid model of Big Hexes

PFont font_hex = createFont("Helvetica", 12, true);

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
void setup() {
  colorMode(RGB, 255);  // HSB colors (not RGB)
  
  size(SCREEN_WIDTH, SCREEN_HEIGHT);
  stroke(0);
  fill(128,128,128);
  
  frameRate(10);
  
  for (int h = 0; h < NUM_HEXES; h++) {
    bigHex[h] = makeBigHex(h);
  }
  
  initializeColorBuffers();  // Stuff curr/next frames with zeros (all black)
  
  _buf = new StringBuffer();
  _server = new Server(this, port);
  println("server listening: " + _server);
}

void draw() {
  pollServer();      // Get messages from python show runner
  drawHexes();       // Re-draw hexes - this is hugely expensive
  pushFrame();
//  print_memory_usage();
}

void drawHexes() {
  for (int h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y) && has_changed(h, x, y)) {
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
    this.c = get_rgb_color(255, 255, 255);
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
    fill(get_red(this.c), get_green(this.c), get_blue(this.c));
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
  // Read 2 different server ports into 2 buffers - keep channels separated
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
// processCommand - process 6 integers as (h, x, y, int rgb)
// x and y are +5 offset, so to be always positive
//
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
  byte i  =    Byte.valueOf(m.group(1));
  byte x  =    Byte.valueOf(m.group(2));  // 0+ (do the offset just before sending)
  byte y  =    Byte.valueOf(m.group(3));  // 0+ (do the offset just before sending)
  int rgb = Integer.valueOf(m.group(4));
  
  next_buffer[i][x][y] = rgb;  
//  println(String.format("setting hex %d coord:%d,%d to r:%d, g:%d, b:%d", i, x, y, get_red(hsv), get_green(hsv), get_blue(hsv)));
}

//
// has_changed - is the next buffer different from the current buffer?
//
boolean has_changed(int h, byte x, byte y) {
  return curr_buffer[h][x][y] != next_buffer[h][x][y];
}


//
// pushFrame
//
void pushFrame() {
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        curr_buffer[h][x][y] = next_buffer[h][x][y];
      }
    }
  }
}


  
void initializeColorBuffers() {
  int black = get_rgb_color(0, 0, 0);
  int gray = get_rgb_color(1, 1, 1);
  
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          curr_buffer[h][x][y] = black;
          next_buffer[h][x][y] = gray;
        }
      }
    }
  }
}

void pushColorBuffer(byte c) {
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          curr_buffer[h][x][y] = next_buffer[h][x][y];
        }
      }
    }
  }
}

int get_rgb_color(int r, int g, int b) {
  return r << 16 | g << 8 | b;
}

short get_red(int c) {
  return (short)(c >> 16 & 0xFF);
}

short get_green(int c) {
  return (short)(c >> 8 & 0xFF);
}

short get_blue(int c) {
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


