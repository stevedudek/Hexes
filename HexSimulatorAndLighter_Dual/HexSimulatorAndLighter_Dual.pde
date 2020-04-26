/*
  Hex Simulator and Lighter
  
  1. Simulator: draws hexes on the monitor
  2. Lighter: sends data to the lights
  
  DUAL SHOWS - Works!
  
  HSV colors (not RGB) for better interpolation
  
  4/11/20
  
  Computer energy is taken up by:
    1. Number of Hexes
    2. Size of the hex screen display
    3. Frame rate (60 >> 30 > 10 frames per second)
    4. Whether the visualizer is on or not (-40% turning off visualizer)
    5. Sending out LED data, polling the server, drawing bottom controls: 
       takes little energy
  
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

import com.heroicrobot.dropbit.registry.*;
import com.heroicrobot.dropbit.devices.pixelpusher.Pixel;
import com.heroicrobot.dropbit.devices.pixelpusher.Strip;
import com.heroicrobot.dropbit.devices.pixelpusher.PixelPusher;
import com.heroicrobot.dropbit.devices.pixelpusher.PusherCommand;

import processing.net.*;
import java.util.*;
import java.util.regex.*;
import java.awt.Color;

int NUM_CHANNELS = 2;  // Dual shows

// network vars
int port = 4444;
Server[] _servers = new Server[NUM_CHANNELS];  // For dual shows 
StringBuffer[] _bufs = new StringBuffer[NUM_CHANNELS];  // separate buffers

class TestObserver implements Observer {
  public boolean hasStrips = false;
  public void update(Observable registry, Object updatedDevice) {
    println("Registry changed!");
    if (updatedDevice != null) {
      println("Device change: " + updatedDevice);
    }
    this.hasStrips = true;
  }
}

TestObserver testObserver;

// Physical strip registry
DeviceRegistry registry;
List<Strip> strips = new ArrayList<Strip>();
Strip[] strip_array = new Strip[NUM_HEXES];

//
// Controller on the bottom of the screen
//
// Draw labels has 3 states:
// 0:LED number, 1:(x,y) coordinate, and 2:none
int DRAW_LABELS = 2;

boolean UPDATE_VISUALIZER = false;  // turn false for LED-only updates

int BRIGHTNESS = 100;  // A percentage

int COLOR_STATE = 0;  // no enum types in processing. Messy
boolean DARK_MODE = false;

// How many little hexes on the base of each big hex
int PIXEL_WIDTH = 11;  // Height & width in pixels (LEDs) of each hex
int HEX_OFFSET = 5;  // Offset to add to hex coordinate to make all coordinates positive
int NUM_PIXELS = PIXEL_WIDTH * PIXEL_WIDTH;
int NUM_LEDS = 106;  // includes spacer leds

// Color buffers: [x][y][r,g,b]
// Two buffers permits updating only the lights that change color
// May improve performance and reduce flickering
int[][][][] curr_buffer = new int[NUM_CHANNELS][NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];
int[][][][] next_buffer = new int[NUM_CHANNELS][NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];
int[][][][] morph_buffer = new int[NUM_CHANNELS][NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];  // blend of curr + next
int[][][] interp_buffer = new int[NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];  // combine two channels here
int[][][] old_final_color = new int[NUM_HEXES][PIXEL_WIDTH][PIXEL_WIDTH];  // to send only changed colors

// Timing variables needed to control regular morphing
// Doubled for 2 channels
int[] delay_time = { 10000, 10000 };  // delay time length in milliseconds (dummy initial value)
long[] start_time = { millis(), millis() };  // start time point (in absolute time)
long[] last_time = { start_time[0], start_time[1] };
short[] channel_intensity = { 255, 0 };  // Off = 0, All On = 255 

// Calculated pixel constants for simulator display
int SCREEN_SIZE = 1200;  // hex screenfloat SMALL_SIZE = (SCREEN_SIZE - 20) / (PIXEL_WIDTH * NUM_HEXES);  // Size of a small hex
int BIG_HEX_WIDTH = (int)(hexHeight() * PIXEL_WIDTH);  // Width of one big hex
int SCREEN_WIDTH = (int)((BIG_HEX_WIDTH) * NUM_HEXES);
int SCREEN_HEIGHT = (int)(vertDistance() * PIXEL_WIDTH) + 20; // Height + a little

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
  size(SCREEN_WIDTH, SCREEN_HEIGHT + 50); // 50 for controls
  stroke(0);
  fill(255,255,0);
  
  frameRate(60);
  
  for (int h = 0; h < NUM_HEXES; h++) {
    bigHex[h] = makeBigHex(h);
  }
  
  registry = new DeviceRegistry();
  testObserver = new TestObserver();
  registry.addObserver(testObserver);
  prepareExitHandler();
  strips = registry.getStrips();
  
  colorMode(HSB, 255);  // HSB colors (not RGB)
  
  initializeColorBuffers();  // Stuff curr/next frames with zeros (all black)
  
  for (int i = 0; i < NUM_CHANNELS; i++) {
    _bufs[i] = new StringBuffer();
    _servers[i] = new Server(this, port + i);
    println("server " + i + " listening: " + _servers[i]);
  }
//  drawHexes();
  drawBottomControls();
}

void draw() {
  pollServer();        // Get messages from python show runner
  update_morph();
  interpChannels();    // Update the visualizer
  if (UPDATE_VISUALIZER) {
    drawHexes();       // Re-draw hexes - this is hugely expensive
  }
  sendDataToLights();  // Dump data into lights
//  print_memory_usage();
}

void drawHexes() {
  for (int h = 0; h < NUM_HEXES; h++) {
    bigHex[h].draw();
  }
}

//
// Bottom Control functions
//
void drawCheckbox(int x, int y, int size, color fill, boolean checked) {
  stroke(0);
  fill(fill);  
  rect(x,y,size,size);
  if (checked) {    
    line(x,y,x+size,y+size);
    line(x+size,y,x,y+size);
  }  
}

void drawBottomControls() {
  // draw a bottom white region
  fill(0,0,255);
  rect(0,SCREEN_HEIGHT,SCREEN_WIDTH,40);
  
  // draw divider lines
  stroke(0);
  line(140,SCREEN_HEIGHT,140,SCREEN_HEIGHT+40);
  line(290,SCREEN_HEIGHT,290,SCREEN_HEIGHT+40);
  line(470,SCREEN_HEIGHT,470,SCREEN_HEIGHT+40);
  
  // draw checkboxes
  stroke(0);
  fill(0,0,255);
  
  // Checkbox is always unchecked; it is 3-state
  rect(20,SCREEN_HEIGHT+10,20,20);  // label checkbox
  
  rect(200,SCREEN_HEIGHT+4,15,15);  // plus brightness
  rect(200,SCREEN_HEIGHT+22,15,15);  // minus brightness
  
  drawCheckbox(340,SCREEN_HEIGHT+4,15, color(255,255,255), COLOR_STATE == 1);
  drawCheckbox(340,SCREEN_HEIGHT+22,15, color(255,255,255), COLOR_STATE == 4);
  drawCheckbox(360,SCREEN_HEIGHT+4,15, color(87,255,255), COLOR_STATE == 2);
  drawCheckbox(360,SCREEN_HEIGHT+22,15, color(87,255,255), COLOR_STATE == 5);
  drawCheckbox(380,SCREEN_HEIGHT+4,15, color(175,255,255), COLOR_STATE == 3);
  drawCheckbox(380,SCREEN_HEIGHT+22,15, color(175,255,255), COLOR_STATE == 6);
  
  drawCheckbox(400,SCREEN_HEIGHT+10,20, color(0,0,255), COLOR_STATE == 0);
  
  // draw text labels in 12-point Helvetica
  fill(0);
  textAlign(LEFT);
  
  textFont(font_hex, 12);
  text("Toggle Labels", 50, SCREEN_HEIGHT+25);
  text("+", 190, SCREEN_HEIGHT+16);
  text("-", 190, SCREEN_HEIGHT+34);
  text("Brightness", 225, SCREEN_HEIGHT+25);
  textFont(font_hex, 20);
  text(BRIGHTNESS, 150, SCREEN_HEIGHT+28);
  
  textFont(font_hex, 12);
  text("None", 305, SCREEN_HEIGHT+16);
  text("All", 318, SCREEN_HEIGHT+34);
  text("Color", 430, SCREEN_HEIGHT+25);
  
  // scale font to size of squares
  textFont(font_hex, 12);
  
}

void mouseClicked() {  
  //println("click! x:" + mouseX + " y:" + mouseY);
  if (mouseX > 20 && mouseX < 40 && mouseY > SCREEN_HEIGHT+10 && mouseY < SCREEN_HEIGHT+30) {
    // clicked draw labels button
    DRAW_LABELS = (DRAW_LABELS + 1) % 3;
   
  }  else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_HEIGHT+4 && mouseY < SCREEN_HEIGHT+19) {
    // Bright up checkbox
    if (BRIGHTNESS <= 95) BRIGHTNESS += 5;
    
  } else if (mouseX > 200 && mouseX < 215 && mouseY > SCREEN_HEIGHT+22 && mouseY < SCREEN_HEIGHT+37) {
    // Bright down checkbox
    BRIGHTNESS -= 5;  
    if (BRIGHTNESS < 1) BRIGHTNESS = 1;
  
  }  else if (mouseX > 400 && mouseX < 420 && mouseY > SCREEN_HEIGHT+10 && mouseY < SCREEN_HEIGHT+30) {
    // No color correction  
    COLOR_STATE = 0;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_HEIGHT+4 && mouseY < SCREEN_HEIGHT+19) {
    // None red  
    COLOR_STATE = 1;
   
  }  else if (mouseX > 340 && mouseX < 355 && mouseY > SCREEN_HEIGHT+22 && mouseY < SCREEN_HEIGHT+37) {
    // All red  
    COLOR_STATE = 4;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_HEIGHT+4 && mouseY < SCREEN_HEIGHT+19) {
    // None blue  
    COLOR_STATE = 2;
   
  }  else if (mouseX > 360 && mouseX < 375 && mouseY > SCREEN_HEIGHT+22 && mouseY < SCREEN_HEIGHT+37) {
    // All blue  
    COLOR_STATE = 5;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_HEIGHT+4 && mouseY < SCREEN_HEIGHT+19) {
    // None green  
    COLOR_STATE = 3;
   
  }  else if (mouseX > 380 && mouseX < 395 && mouseY > SCREEN_HEIGHT+22 && mouseY < SCREEN_HEIGHT+37) {
    // All green  
    COLOR_STATE = 6;
    
  }
  drawBottomControls();
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
    this.c = get_hsv_color(255, 255, 255);
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
  // Read 2 different server ports into 2 buffers - keep channels separated
  for (int i = 0; i < NUM_CHANNELS; i++) {
    try {
      Client c = _servers[i].available();
      // append any available bytes to the buffer
      if (c != null) {
        _bufs[i].append(c.readString());
      }
      // process as many lines as we can find in the buffer
      int ix = _bufs[i].indexOf("\n");
      while (ix > -1) {
        String msg = _bufs[i].substring(0, ix);
        msg = msg.trim();
        processCommand(msg);
        _bufs[i].delete(0, ix+1);
        ix = _bufs[i].indexOf("\n");
      }
    } catch (Exception e) {
      println("exception handling network command");
      e.printStackTrace();
    }
  }  
}

//
// With DUAL shows: 
// 1. all commands must start with either a '0' or '1'
// 2. Followed by either
//     a. X = Finish a morph cycle (clean up by pushing the frame buffers)
//     b. D(int) = delay for int milliseconds (but keeping morphing)
//     c. I(short) = channel intensity (0 = off, 255 = all on)
//     d. Otherwise, process 6 integers as (i,x,y, int hsv)
//
//
void processCommand(String cmd) {
  if (cmd.length() < 2) { return; }  // Discard erroneous stub characters
  byte channel = (cmd.charAt(0) == '0') ? (byte)0 : (byte)1 ;  // First letter indicates Channel 0 or 1
  cmd = cmd.substring(1, cmd.length());  // Strip off first-letter Channel indicator
  
  if (cmd.charAt(0) == 'X') {  // Finish the cycle
    finishCycle(channel);
  } else if (cmd.charAt(0) == 'D') {  // Get the delay time
    delay_time[channel] = Integer.valueOf(cmd.substring(1, cmd.length()));
  } else if (cmd.charAt(0) == 'I') {  // Get the intensity
    channel_intensity[channel] = Integer.valueOf(cmd.substring(1, cmd.length())).shortValue();
  } else {  
    processPixelCommand(channel, cmd);  // Pixel command
  }
}

// 4 comma-separated numbers for i, x, y, color
Pattern cmd_pattern = Pattern.compile("^\\s*(\\d+),(\\d+),(\\d+),(\\d+)\\s*$");

void processPixelCommand(byte channel, String cmd) {
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    //println(cmd);
    println("ignoring input for " + cmd);
    return;
  }
  byte i  =    Byte.valueOf(m.group(1));
  byte x  =    Byte.valueOf(m.group(2));  // 0+ (do the offset just before sending)
  byte y  =    Byte.valueOf(m.group(3));  // 0+ (do the offset just before sending)
  int hsv = Integer.valueOf(m.group(4));
  
  next_buffer[channel][i][x][y] = hsv;  
//  println(String.format("setting channel %d hex %d coord:%d,%d to h:%d, s:%d, v:%d", channel, i, x, y, get_hue(hsv), get_sat(hsv), get_val(hsv)));
}

//
// Finish Cycle
//
// Get ready for the next morph cycle by morphing to the max and pushing the frame buffer
//
void finishCycle(byte channel) {
  morph_frame(channel, 1.0);  // May work after all
  pushColorBuffer(channel);
  start_time[channel] = millis();  // reset the clock
}

//
// Update Morph
//
void update_morph() {
  // Fractional morph over the span of delay_time
  for (byte channel = 0; channel < NUM_CHANNELS; channel++) {
    last_time[channel] = millis();  // update clock
    float fract = (last_time[channel] - start_time[channel]) / (float)delay_time[channel];
    if (is_channel_active(channel) && fract <= 1.0) {
      morph_frame(channel, fract);
    }
  }
}

//
// Is Channel Active
//
boolean is_channel_active(int channel) {
  return (channel_intensity[channel] > 0);
}

/////  Routines to interact with the Lights

//
// Interpolate Channels
//
// Interpolate between the 2 channels
// Push the interpolated results on to the simulator 
//
void interpChannels() {
  if (!is_channel_active(0)) {
    pushOnlyOneChannel(1);
  } else if (!is_channel_active(1)) {
    pushOnlyOneChannel(0);
  } else {
    float fract = (float)channel_intensity[0] / (channel_intensity[0] + channel_intensity[1]);
    morphBetweenChannels(fract);
  }
}

//
// pushOnlyOneChannel - push the morph_channel to the simulator
//
void pushOnlyOneChannel(int channel) {
  int col;
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          col = adjColor(morph_buffer[channel][h][x][y]);
          bigHex[h].setCellColor(col, x, y);
          interp_buffer[h][x][y] = col;
        }
      }
    }
  }
}

//
// morphBetweenChannels - interpolate the morph_channel on to the simulator
//
void morphBetweenChannels(float fract) {
  int col;
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          col = adjColor(interp_color(morph_buffer[1][h][x][y], morph_buffer[0][h][x][y], fract));
          bigHex[h].setCellColor(col, x, y);
          interp_buffer[h][x][y] = col;
        }
      }
    }
  }
}

// Adjust color for brightness and hue
int adjColor(int c) {
  return adj_brightness(colorCorrect(c));
}

//
//  Routines for the strip buffer
//
void sendDataToLights() {
  sendChangedDataToLights();
  pushFinalBuffer();
}

void pushFinalBuffer() {
  // Push the new_final_color buffer on to the old_final_color buffer
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          old_final_color[h][x][y] = interp_buffer[h][x][y];
        }
      }
    }
  }
}

void sendChangedDataToLights() {
  if (testObserver.hasStrips) {   
    registry.startPushing();
    registry.setExtraDelay(0);
    registry.setAutoThrottle(true);
    registry.setAntiLog(true);    
    
    byte h = 0;
    
    List<Strip> strips = registry.getStrips();
    
    for (Strip strip : strips) {
      for (byte x = 0; x < PIXEL_WIDTH; x++) {
        for (byte y = 0; y < PIXEL_WIDTH; y++) {
          if (bigHex[h].hexExists(x,y)) {
            strip.setPixel(hsv_to_rgb(interp_buffer[h][x][y]), bigHex[h].getLED(x,y));
          }
        }
      }
    h++;
    if (h >= NUM_HEXES) break;  // Prevents buffer overflow 
    }
  }
}

private void prepareExitHandler () {

  Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {

    public void run () {

      System.out.println("Shutdown hook running");

      List<Strip> strips = registry.getStrips();
      for (Strip strip : strips) {
        for (int i = 0; i < strip.getLength(); i++)
          strip.setPixel(#000000, i);
      }
      for (int i=0; i<100000; i++)
        Thread.yield();
    }
  }
  ));
}

//
//  Fractional morphing between current and next frame - sends data to lights
//
//  fract is an 0.0 - 1.0 fraction towards the next frame
//
void morph_frame(byte c, float fract) {
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          morph_buffer[c][h][x][y] = interp_color(curr_buffer[c][h][x][y], next_buffer[c][h][x][y], fract);
        }
      }
    }
  }
}

int adj_brightness(int c) {
  // Adjust only the 3rd brightness/value channel
  return get_hsv_color(get_hue(c), 
                       get_sat(c),
               (short)(get_val(c) * BRIGHTNESS / 100));
}

int colorCorrect(int c) {
  short old_hue = get_hue(c);
  short new_hue;
  
  switch(COLOR_STATE) {
    case 1:  // no red
      new_hue = map_range(old_hue, 40, 200);
      break;
    
    case 2:  // no green
      new_hue = map_range(old_hue, 120, 45);
      break;
    
    case 3:  // no blue
      new_hue = map_range(old_hue, 200, 120);
      break;
    
    case 4:  // all red
      new_hue = map_range(old_hue, 200, 40);
      break;
    
    case 5:  // all green
      new_hue = map_range(old_hue, 40, 130);
      break;
    
    case 6:  // all blue
      new_hue = map_range(old_hue, 120, 200);
      break;
    
    default:  // all colors
      new_hue = old_hue;
      break;
  }
  return get_hsv_color(new_hue, get_sat(c), get_val(c));
}

//
// map_range - map a hue (0-255) to a smaller range (start-end)
//
short map_range(float hue, int start, int end) {
  int range = (end > start) ? end - start : (end + 256 - start) % 256 ;
  return (short)((start + ((hue / 255.0) * range)) % 256);
}
  
void initializeColorBuffers() {
  for (int c = 0; c < NUM_CHANNELS; c++) {
    fill_black_one_channel(c);
  }
}

void fill_black_one_channel(int c) {
  int black = get_hsv_color(255,0,255);
  
  for (byte h = 0; h < NUM_HEXES; h++) {
    for (byte x = 0; x < PIXEL_WIDTH; x++) {
      for (byte y = 0; y < PIXEL_WIDTH; y++) {
        if (bigHex[h].hexExists(x,y)) {
          curr_buffer[c][h][x][y] = black;
          next_buffer[c][h][x][y] = black;
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
          curr_buffer[c][h][x][y] = next_buffer[c][h][x][y];
        }
      }
    }
  }
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

int hsv_to_rgb(int c) {
  // Convert an hsv int to an rgb int
  return Color.HSBtoRGB(float(get_hue(c)) / 255.0,
                        float(get_sat(c)) / 255.0,
                        float(get_val(c)) / 255.0);
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

int interp_color(int c1, int c2, float fract) {
 // brute-force color interpolation
 if (c1 == c2) {
   return c1;
 } else if (fract <= 0) {
   return c1;
 } else if (fract >= 1) {
   return c2;
 } else {
   return get_hsv_color(interp_wrap(get_hue(c1), get_hue(c2), fract),
                             interp(get_sat(c1), get_sat(c2), fract),
                             interp(get_val(c1), get_val(c2), fract));
 }
}

short interp(short a, short b, float fract) {
  if (a == b) return a;
  if (fract <= 0) return a;
  if (fract >= 1) return b;
  if (b == 0) return (short)DIM_AMOUNT[int(a * fract)];
  if (a == 0) return (short)DIM_AMOUNT[int(b * fract)];
  return (short)(a + fract * (b - a));
}

short interp_wrap(short a, short b, float fract) {
  if (a == b) return a;
  if (fract <= 0) return a;
  if (fract >= 1) return b;
  
  float distCCW, distCW, answer;

  if (a >= b) {
    distCW = 256 + b - a;
    distCCW = a - b;
  } else {
    distCW = b - a;
    distCCW = 256 + a - b;
  }
  if (distCW <= distCCW) {
    answer = a + (distCW * fract);
  } else {
    answer = a - (distCCW * fract);
    if (answer < 0) {
      answer += 256;
    }
  }
  return (short)answer;
}

