import builtins

import zerorpc

import zkillboard2excel

def main():
    client = zerorpc.Client()
    client.connect('tcp://0.0.0.0:4242')
    builtins.print = client.log

    print('Start')

    zkillboard2excel.run()

    print('Done')

    client.kill()

if __name__ == '__main__':
    main()
