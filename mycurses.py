import curses
import math

stdscr = None
processWindow = None
msgWindow = None
dataWin = None

def killCurses() :
  global stdscr
  curses.nocbreak()
  stdscr.keypad(0)
  curses.echo()
  curses.endwin()


def initCurses() :
  global stdscr
  stdscr = curses.initscr()
  curses.noecho()
  curses.cbreak()
  stdscr.keypad(1)
  
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
  msgWindow.refresh()

  dataWin = curses.newwin(curses.LINES - py -2, math.ceil(curses.COLS*2/3),
      py+1, math.ceil(curses.COLS/3)+1)
  dataWin.box()
  dataWin.refresh()

def writeOnWindow(win, msg, indent=1, overwrite=False
    , appendNewLine=True) :
  win.scrollok(True)
  y, x = win.getyx()
  if overwrite : 
    x = 0
  if appendNewLine :
    msg += "\n"
  assert y >= 0, x >= 0
  win.addstr(int(y),int(x+indent),str(msg))
  win.box()
  win.refresh()

