"""Merge Socrata API CSV pages into the portal-export format build.py expects."""
import sys,glob,pandas as pd
HDR="Taxpayer Number,Taxpayer Name,Taxpayer Address,Taxpayer City,Taxpayer State,Taxpayer Zip,Taxpayer County Code,Taxpayer Organizational Type,Record Type Code,Responsibility Beginning Date,  Secretary of State (SOS) or COA File Number,SOS Charter Date,SOS Status Date ,SOS Status Code,Right to Transact Business Code,Current Exempt Reason Code,Exempt Begin Date,NAICS Code".split(",")
dates={9,11,12,16}
out=sys.argv[-1]; first=True
for f in sorted(sys.argv[1:-1]):
    for ch in pd.read_csv(f,dtype=str,chunksize=200000,keep_default_na=False):
        ch=ch.apply(lambda c:c.str.strip())
        for i in dates:
            c=ch.columns[i]; d=pd.to_datetime(ch[c],errors='coerce'); ch[c]=d.dt.strftime('%m/%d/%Y').fillna('')
        ch.columns=HDR; ch.to_csv(out,mode='w' if first else 'a',header=first,index=False); first=False
