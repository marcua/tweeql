from ssql.query_runner import QueryRunner
from ssql.query_runner import DbInsertStatusHandler
from ssql.builtin_functions import register
from time import sleep

def main():
    register()
    insert_handler = DbInsertStatusHandler('tester2', 'sqlite:///test.db')
    runner = QueryRunner(insert_handler, batch_size=10)
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
