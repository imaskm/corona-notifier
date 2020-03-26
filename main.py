import logging,argparse,datetime,requests,json,time
from bs4 import BeautifulSoup
import notify2  



FORMAT =  '[%(asctime)-15s] %(message)s'
MOHFW_URL = 'https://www.mohfw.gov.in/'
SHORT_HEADERS = ['S.N.', 'State', 'Ind','Fnrs' ,'Cd','Dth']
DATA_FILE = 'india_data.json'
ExtractData = lambda lines: [ x.text.replace('\n','') for x in lines]

logging.basicConfig(format=FORMAT,level=logging.DEBUG,filename='corona.log',filemode='a')

def get_past_data():

    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_current_data(data):
    with open(DATA_FILE,'w') as f:
        json.dump(data,f)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--states',default='')

    args = parser.parse_args()
    interested_states = args.states.split(',')
    
    current_time = datetime.datetime.now().strftime('%d-%m-%Y  %H:%M')

    try:
        response=  requests.get(MOHFW_URL).content

        souped_data = BeautifulSoup(response,'html.parser')
        #getting the headers of table
        souped_data = BeautifulSoup(str(souped_data.find_all('div',{'class': "content newtab"})),'html.parser')
        
        headers = ExtractData(souped_data.tr.find_all('th'))

        stats=[]

        #get all rows of tables
        all_rows= souped_data.find_all('tr')

        for row in all_rows:

            columns = ExtractData(row.find_all('td'))
            if columns:
                #if 5 then it's last row
                if(len(columns) == 5):

                    columns.insert(0,'')
                    stats.append(columns)
                    break
                elif any([s.lower() in columns[1].lower() for s in interested_states]):
                    stats.append(columns)

        past_data = get_past_data()

        current_data = { x[1]:x[2:] for x in stats }

        changed = False

        info = []

        for state in current_data:

            if state not in past_data:

                info.append(f'New State {state} got effected with corona virus: { current_data[state] }')
                changed = True
            else:
                past = past_data[state]
                current = current_data[state]
                if( past != current ):
                    changed = True
                    info.append(f'Stats changed for state {state}:  {past} -> {current}')

        events_info = ''

        for event in info:
            logging.info(event)

            events_info+="\n - "+event
        import pdb
        pdb.set_trace()

        if changed:
            save_current_data(current_data)
            notify2.init('Corona Virus in India')
            
            n = notify2.Notification("Corona Info",events_info)
            n.set_urgency(notify2.URGENCY_NORMAL)
            n.show()
            time.sleep(60)

    except Exception as e:
        logging.exception('oops, corono script failed.')
        
        
                




                    
















