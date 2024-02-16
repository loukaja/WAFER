# API endpoint URL and grant_type parameter
URL = 'https://auth.tidal.com/v1/oauth2/token'
PARAMS = {'grant_type': 'client_credentials'}

# Months
KK_BASE = ['Tammikuu', 'Helmikuu', 'Maaliskuu', 'Huhtikuu', 'Toukokuu',
           'Kesäkuu', 'Heinäkuu', 'Elokuu', 'Syyskuu', 'Lokakuu', 'Marraskuu', 'Joulukuu']
KK = ['tammikuuta', 'helmikuuta', 'maaliskuuta', 'huhtikuuta', 'toukokuuta', 'kesäkuuta',
      'heinäkuuta', 'elokuuta', 'syyskuuta', 'lokakuuta', 'marraskuuta', 'joulukuuta']
SUPPORTED_DOMAINS = ['kaaoszine.fi', 'www.soundi.fi',
                     'metalliluola.fi', 'blabbermouth.net', 'metalinjection.net', 'www.metalsucks.net']
