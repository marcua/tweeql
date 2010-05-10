from ssql.query_runner import QueryRunner
from ssql.query_runner import PrintStatusHandler
from time import sleep

def main():
    runner = QueryRunner(PrintStatusHandler(), 10)
    try:
        while True:
            cmd = raw_input("ssql> ");
            process_command(runner, cmd)
    except KeyboardInterrupt:
        print '\nGoodbye!'

def process_command(runner, cmd):
    try:
        runner.run_query(cmd)
        while True:
            sleep(1000)
    except KeyboardInterrupt:
        runner.stop_query()

if __name__ == '__main__':
    main()
