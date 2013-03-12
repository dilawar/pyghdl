import curses
import math

stdscr = None
processWindow = None
msgWindow = None
dataWindow = None

def formatString(msg, width) :
  newmsg = ""
  loopIndex = math.ceil(len(msg) / width)
  for i in range(0, loopIndex) :
    if i == loopIndex :
      newmsg += msg[width*i:]
    else :
      newmsg += msg[width*i : (i+1)*width+1]
      newmsg += "\n"
  return newmsg


def killCurses() :
  global stdscr
  curses.nocbreak()
  stdscr.keypad(0)
  curses.echo()
  curses.endwin()


def initCurses() :
  global stdscr
  stdscr = curses.initscr()
  curses.start_color()
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(1)

  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
  
  global processWindow
  processWindow = curses.newwin(10,curses.COLS,0,0)
  processWindow.idlok(1)
  processWindow.scrollok(1)
  processWindow.box()
  processWindow.refresh()

  py, px = processWindow.getmaxyx()
  global msgWindow
  msgWindow = curses.newwin(curses.LINES - py - 2, math.ceil(curses.COLS/3),
      py + 1, 0)
  msgWindow.box()
  msgWindow.idlok(1)
  msgWindow.scrollok(1)
  msgWindow.refresh()

  global dataWindow
  dataWindow = curses.newwin(curses.LINES - py -2, math.ceil(curses.COLS*2/3),
      py+1, math.ceil(curses.COLS/3)+1)
  dataWindow.idlok(1)
  dataWindow.scrollok(1)
  dataWindow.box()
  dataWindow.refresh()

def writeOnWindow(win, msg, indent=1, overwrite=False
    , appendNewLine=True, opt=None) :
  maxY, maxX = win.getmaxyx()
  y, x = win.getyx()
  if overwrite : 
    x = 0
  if appendNewLine :
    msg += "\n"
  assert y >= 0, x >= 0
  msg = formatString(msg, maxX-3-indent)
  if opt :
    win.addstr(int(y),int(x+indent),str(msg), opt)
  else :
    win.addstr(int(y),int(x+indent),str(msg))
  win.box()
  win.refresh()

