import sys
from optparse import OptionParser
import os
from j1.traffic_sign_recognition import Job1
from j2.line_detection import Job2


if __name__ == "__main__":
    server_ip = os.getenv('SERVER_IP')
    
    if server_ip is None:
        print('server ip not defined')
        sys.exit(1)
    
    parser = OptionParser()
    parser.add_option("-j", "--job", dest="job")
    parser.add_option("-i", "--input", dest="input_directory")

    options, args = parser.parse_args()
    print(options.job)
    if options.job == "1":
        job = Job1(server_ip, options.input_directory)
        job.main()
    elif options.job == "2":
        job = Job2(server_ip)
        job.main()
