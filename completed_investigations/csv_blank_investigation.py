import sys

#GOAL: I've confirmed that having blank lines in the book database is the root cause of the prepare_scope method failing.
    #Presumably, these blank lines cause pandas to misidentify the data type when it loads in the csv, although the mechanism doesn't really matter much.
#I would like to figure out what creates these blank lines.
#I can see from the time stamps that these blank lines seperate some (but not all) Data_Collection runs.
#Because the data collector starts the same way every time, I am assuming that these blank lines are created at termination. There are various ways the function can terminate:
    #When the function completes and calls .close()
    #When the function has an error and terminates early.
    #When I do a keyboardInterrupt.
    #although i'm not certain, I assume that an error, a keyboard interrupt, and a sys.exit have the same impact.
    ##TO START, I WANT TO TEST THESE SCENARIOS ONLY:
        #NATURAL TERMINATION OF CODE WITH CLOSE
        #NATURAL TERMINATION OF CODE WITHOUT CLOSE
        #EARLY TERMINATION THROUGH SYS EXIT

##RESULTS
    #FIRST TEST: CLOSE VS NO CLOSE:
        #blank line was created once, at start of file. Why would that be?
        #Ran the same code again, still just the single line.
        #HYPOTHESIS: Blank line is created only when running open on a file that doesn't exist...but that's not possible beause the blanks appear in the middle of my log file.

        #WHAT ELSE IS DIFFERENT THE FIRST TIME THE FILE IS OPENED?
        #WHEN \n is written, where does it go?

##TESTING

def csv_tester(file_name, text_string, num_repeats, close = True):

    log_file_name = file_name + ".csv"
    log_file =open(log_file_name, "a")

    for i in range(0, num_repeats):
        log_file.write("\n" + text_string)

    if close:
        log_file.close()

csv_tester("csv_blank_investigation_log", "natural termination w/ close: run1", 5)
csv_tester("csv_blank_investigation_log", "natural termination w/ close: run2", 5)

csv_tester("csv_blank_investigation_log", "natural termination w/o close: run1", 5, close = False)
csv_tester("csv_blank_investigation_log", "natural termination w/o close: run2", 5, close = False)
