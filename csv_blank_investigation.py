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

def csv_tester(file_name, print_string):

    pass 
