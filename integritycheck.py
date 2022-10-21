
import argparse
import pandas
import subprocess
import command

integrityArray = []

def writeToExcel(arrayName,fileName,sheetName):
    writer = pandas.ExcelWriter(fileName, engine='xlsxwriter')
    df=pandas.json_normalize(arrayName)
    pandas.set_option('display.max_rows', df.shape[0]+1)
    df.to_excel(writer, sheet_name=sheetName,index = False)
    writer.save()


def run_rclone_md5sum(remotePath,rcloneconf,fileName):
    try:
        outfile = open(fileName, "a")
        cmd = ['rclone', 'md5sum', '--config', rcloneconf, '--fast-list', remotePath]
        p = subprocess.Popen(cmd, stdout=outfile)  
    except Exception as e:
        print(e)

def generateHashandCompare(srcFile,dstFile):
    global integrityArray
    try:
        srcDict = {}
        srcArray = open(srcFile,'r').readlines()

        destDict = {}
        destArray = open(dstFile,'r').readlines()

        for item in srcArray:
            item = item.strip()
            srcDict[item.split(' ')[2]] = item.split(' ')[0]

        for item in destArray:
            item = item.strip()
            destDict[item.split(' ')[2]] = item.split(' ')[0]


        if len(srcDict) == len(destDict):
            if srcDict == destDict:
                print("The source and Destination Dictionaries are Equal")
            else:
                print("The source and Destination Dictionaries are not Equal")

            for key in srcDict.keys():
                item = {}
                item['File'] = key
                item['SrcMD5Hash'] = srcDict[key]
                if key in destDict:
                    item['DestMD5Hash'] = destDict[key]
                else:
                    item['DestMD5Hash'] = None
                if item['DestMD5Hash'] == item['SrcMD5Hash']:
                    item['Status'] = 'Success'
                else:
                    item['Status'] = 'Failure'

                integrityArray.append(item)
            
        else:
            print("The source and Destination Dictionaries are not Equal in Length")    
    except Exception as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NS Migration Manager')
    parser.add_argument('--srcpath',required=True, default=None,help='Source Path')
    parser.add_argument('--destpath',required=True, default=None,help='Destination Path')
    parser.add_argument('--rcloneconf',required=True, default=None,help='rclone Conf Path')

    args = parser.parse_args()
    print(args)


    run_rclone_md5sum(args.srcpath,args.rcloneconf,'srcmd5.txt')
    run_rclone_md5sum(args.destpath,args.rcloneconf,'destmd5.txt')
    generateHashandCompare('srcmd5.txt','destmd5.txt')
    print("Done!!")
    writeToExcel(integrityArray,'result.xlsx','migration')


'''
python3 integritycheck.py --srcpath 'acmptest:/845028/timessrc' --destpath 'acmptestzip:/1343206/timesdest' --rcloneconf '/Users/apadmana/.config/rclone/rclone.conf'
'''

#