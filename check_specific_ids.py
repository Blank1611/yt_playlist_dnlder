import os
import re

# Archive IDs to check
archive_entries = [
    ('50VNCymT-Cs', 'Alec Benjamin - Let Me Down Slowly [Official Music Video]'),
    ('BVXtQxkCrdU', 'Rauf Faik - evenings (Official video)'),
    ('Ca7bpSr3N6M', '@omri  - Save Me'),
    ('Eh0N0OVluTc', 'Besomorph - Natalie Don\'t (ft. Olivia Kierdal)'),
    ('FRNYQeQ6AZA', 'Mzade - Always (Original Mix)'),
    ('FsnluXPC6s0', 'ASHWOOD - Maria (ft. Blooom & Ghost\'n\'Ghost) | Electronic Pop | NCS - Copyright Free Music'),
    ('Ma6n51jlCHM', 'Asadov - Dark Sun (Original Mix)'),
    ('N9RrlA69WvU', 'SOFI TUKKER & John Summit - Sun Came Up (Official Video) [Ultra Records]'),
    ('UnlM3c1y3Wk', 'Vanotek Feat. Eneli - Back To Me (Robert Cristian Remix)'),
    ('Xs0Lxif1u9E', 'RADWIMPS - Suzume feat. Toaka [Official Lyric Video]'),
    ('ZH9JyEkr2NY', 'Realize | SNX'),
    ('gHUm-6IvgCg', 'Vanotek feat. Eneli - Back to Me | Official Video'),
    ('m-el0pQLQE4', 'Rauf & Faik - childhood (Official video)'),
    ('mlZIB5NOE7E', 'Besomorph - Sweet Dreams【GMV】'),
    ('oY9Dg-OlA3E', 'the devil\'s violinist Paganini'),
    ('r0bO9CKb0Wo', 'YA NINA - Sugar (Cover)'),
    ('xVKGXgHDMvQ', 'Hooverphonic - Mad About You (Official Video)')
]

# Get all mp4 files from Awesome_testing directory
download_path = r'E:\2tbhdd\songs\syst\New folder\youtube\Awesome_testing'
files = [f for f in os.listdir(download_path) if f.endswith('.mp4')]

# Extract video IDs from filenames
id_pattern = re.compile(r'\[([a-zA-Z0-9_-]{11})\]')

print('=' * 80)
print('CHECKING ARCHIVE IDs vs FILE IDs')
print('=' * 80)

matches = 0
no_matches = 0

for archive_id, title in archive_entries:
    print(f'\nArchive ID: [{archive_id}]')
    print(f'Title: {title}')
    
    # Search for this ID in files
    found = False
    for file in files:
        match = id_pattern.search(file)
        if match:
            file_id = match.group(1)
            if file_id == archive_id:
                print(f'  ✓ MATCH FOUND')
                print(f'  File: {file[:100]}')
                found = True
                matches += 1
                break
    
    if not found:
        # Check if any file has similar title (first 3 significant words)
        title_words = [w for w in title.split() if len(w) > 3][:3]
        matching_files = []
        
        for f in files:
            if any(word.lower() in f.lower() for word in title_words):
                matching_files.append(f)
        
        if matching_files:
            print(f'  ✗ NO MATCH - But found similar files:')
            for mf in matching_files[:2]:
                match = id_pattern.search(mf)
                if match:
                    print(f'    File ID: [{match.group(1)}]')
                    print(f'    File: {mf[:80]}...')
        else:
            print(f'  ✗ NO MATCH - File not found')
        no_matches += 1

print('\n' + '=' * 80)
print(f'SUMMARY: {matches} matches, {no_matches} no matches out of {len(archive_entries)} total')
print('=' * 80)
