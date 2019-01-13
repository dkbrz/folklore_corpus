import os

def mdb_csv(filename):
	directory = './'+os.path.dirname(filename.replace('.mdb',''))
    if not os.path.exists(directory):
        os.makedirs(directory)
    
os.system('.')
mdb-export /home/dkbrz/Downloads/Zlynkovsk2016-2018.mdb tblCards -d '\t' > tblCards.csv
mdb-export /home/dkbrz/Downloads/Zlynkovsk2016-2018.mdb tblInformators -d '\t' > tblInformators.csv
mdb-export /home/dkbrz/Downloads/Zlynkovsk2016-2018.mdb tblSobirately -d '\t' > tblSobirately.csv
