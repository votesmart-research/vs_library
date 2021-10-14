
# Key-value pair between office_id and name of office from the 'office' table
# Queried from: SELECT office_id, name FROM office ORDER BY rank LIMIT(9)
OFFICE = {
        '1': 'President',
        '2': 'Vice President',
        '3': 'Governor',
        '4': 'Lieutenant Governor',
        '5': 'U.S. House',
        '6': 'U.S. Senate',
        '7': 'State Assembly',
        '8': 'State House',
        '9': 'State Senate',
        '12': 'Attorney General',
        '44': 'Secretary of State',
        '78': 'Chief Justice of the Supreme Court',
        '79': 'Justice of the Supreme Court'
    }

# Key-value pair between officetype_id and type of office from the 'officetype' table
# Queried from: SELECT officetype_id, name FROM officetype WHERE officelevel_id != 'L' ORDER BY rank
OFFICE_TYPE = {
        'P': 'Presidential',
        'C': 'Congressional',
        'G': 'Gubernatorial',
        'L': 'State Legislative',
        'J': 'Federal Judicial',
        'S': 'Statewide',
        'K': 'State Judicial',
    }

# Key-value pair between electionstage_id and stages of election from the 'electionstage' table
# Queried from: SELECT electionstage_id, name, FROM electionstage
ELECTION_STAGE = {
    'P': 'Primary',
    'G': 'General',
    'Q': 'Primary Runoff',
    'R': 'General Runoff'
    }

# Key-value pair between ratingformat_id and format of ratings from the 'ratingformat' table
# Queried from: SELECT * FROM ratingformat
RATING_FORMAT = {
    '1': 'Numeric',
    '2': 'Grades',
    '3': 'Rating String',
    '-1': 'Open'
    }

# Key-value pair between ratingsession_id and the available legislative session from the 'ratingsession' table
# Queried from: SELECT * FROM ratingsession
RATING_SESSION = {
    '1': 'First Session',
    '2': 'Second Session',
    '3': 'Full Session',
    '-1': '#N/A or Unknown'
    }

# Key-value pair between finance campaign organization with its given ids from the 'finsource' table
# Queried from: SELECT finsource_id, name FROM finsource
FINSOURCE = {
    '1': 'OpenSecrets.org',
    '2': 'Federal Election Commision',
    '3': 'FollowTheMoney.org',
    '4': 'FollowTheMoney.org v2'
    }

# Key-value pair between state abbreviation and state name from the 'state' table
# Queried from: SELECT state_id, name FROM state
STATE = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
    'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
    'MH': 'Marshall Islands', 'NA': 'National', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
    'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}