#!/usr/bin/env python

################################################################################
#$Id: data_schema.py,v 1.450 2017/11/23 09:50:31 aman.puniyani Exp $
#Copyright(c) 2013 Veveo.tv
################################################################################

# Various separators

import re
from copy import copy
from fast_autocomplete.kg.data_constants import (
    CONTENT_TYPE_RATING, CONTENT_TYPE_LANGUAGE, CONTENT_TYPE_GENRE,
    CONTENT_TYPE_FILTER, CONTENT_TYPE_DECADE, CONTENT_TYPE_TOURNAMENT,
    CONTENT_TYPE_TEAM, CONTENT_TYPE_SPORTS_GROUP, CONTENT_TYPE_STADIUM,
    CONTENT_TYPE_PHRASE, CONTENT_TYPE_AWARD, CONTENT_TYPE_PERSON,
    CONTENT_TYPE_MOVIE, CONTENT_TYPE_TVSERIES, CONTENT_TYPE_EPISODE,
    CONTENT_TYPE_SEQUEL, CONTENT_TYPE_TVVIDEO, CONTENT_TYPE_ROLE,
    CONTENT_TYPE_SPORT, CONTENT_TYPE_CHANNEL, CONTENT_TYPE_CHANNEL_AFFILIATION,
    CONTENT_TYPE_REGION, CONTENT_TYPE_PC, CONTENT_TYPE_OAC
)

RECORD_SEPARATOR          = '#<>#'
FIELD_SEPARATOR           = '<>'
VALUE_SEPARATOR           = FIELD_SEPARATOR
PAIRS_SEPARATOR           = '<<>>'
MOVIE_CAST_PAIR_SEPARATOR = '<<>>'
SEED_PARENT_FIELD         = 'Pi'
PARENT_FIELD              = 'Mi'

TRIPLE_SHARP              = '###'
AKA_SEPARATOR             = TRIPLE_SHARP
DIFF_SEPARATOR            = TRIPLE_SHARP
TVS_EN_SN_RULE_SEPARATOR  = TRIPLE_SHARP

SHARP                     = '#'
SEQUEL_PART_SEPARATOR     = SHARP
RD_KEY_VALUE_SEPARATOR    = SHARP

RULE_SEPARATOR            = '##<>##'
RULE_VALUE_SEPARATOR      = '##:<>:##'
RULE_FIELD_SEPARATOR      = ':::'

DOMAIN_SEPARATOR          = ';'

TILDE                     = '~'
HYPHEN                    = '-'

COMMA                     = ','
VERSION_SEPARATOR         = COMMA
VERSION_ID_SEPARATOR      = ': '

PIPE_SEPARATOR            = '|'
ROVI_INPUT_FILE_SEPARATOR = PIPE_SEPARATOR

WR_SCREENPLAY_WRITER_TAG  = 'sp'
WR_AUTHOR_TAG             = 'au'
WR_STORY_BY_TAG           = 'sb'
WR_CREATOR_TAG            = 'cr'
# list various schemas of the different data sources and spaces.

def get_schema(fields):
    return dict(list(zip(fields, list(range(len(fields))))))

def get_indices(fields, schema):
    return (schema.get(field) for field in fields)

class SchemaAccessor:
    def __init__(self, schema):
        self.len = 0
        for attr, pos in schema.items():
            setattr(self, attr, pos)
            self.len += 1

    def __len__(self):
        return self.len

    def __getitem__(self, field):
        return getattr(self, field)

    def add_field(self, field):
        try:
            return getattr(self, field)
        except:
            setattr(self, field, self.len)
            self.len += 1
            return self.len - 1

# CATALOGUE MATCHING SCHEMA
CATALOGUE_MATCHING_SCHEMA_FIELDS = ['Gi', 'Ti', 'Ep', 'Sn', 'En', 'Ca', \
                                'De', 'Ry', 'Mi', 'So', 'Ge', 'Ra', \
                                'Vt', 'Du', 'Sk', 'Ll', 'Pv', 'Cg', \
                                'St', 'Et', 'Pe', 'Hi', 'Hd', 'Dm', \
                                'Aa', 'Pd', 'An', 'Ak', 'Fd', 'Fy', \
                                'Di', 'Pr', 'Od', 'Ae', 'Zl', 'Tg', \
                                'Av', 'Xa', 'Ot', 'Mt', 'At', 'Cp', \
                                'Pp', 'Oa', 'Oe', 'As', 'Pa', 'Tl', \
                                'Hc', 'Xi', 'Xt', 'Cl', 'Um', 'Zc', \
                                'Tr', 'Md', 'Sr']
CATALOGUE_MATCHING_SCHEMA      = get_schema(CATALOGUE_MATCHING_SCHEMA_FIELDS)

# Used in IMDB MC file
IMDB_SCHEMA_FIELDS             = ['Gi', 'Ti', 'Vt', 'Ak', 'Ca', 'Ce', \
                                'Ci', 'Cl', 'De', 'Di', 'Du', 'Ds', \
                                'En', 'Ep', 'Fa', 'Ge', 'Go', 'Ho', \
                                'Ke', 'La', 'Ll', 'Nv', 'Od', 'Ot', \
                                'Pc', 'Pi', 'Pr', 'Qu', 'Ra', 'Re', \
                                'Ro', 'Ry', 'Sn', 'Tg', 'Tk', 'Tl', \
                                'Tr', 'Uk', 'Wr', 'Aa', 'Uc', 'Ek', \
                                'Kt', 'Xr', 'Bi', 'Co', 'Bd', 'Br', \
                                'Sx', 'Ki']
IMDB_SCHEMA                    = get_schema(IMDB_SCHEMA_FIELDS)

IMDB_FOLD_SCHEMA_FIELDS        = ['Gi', 'Ti', 'Ty', 'De', 'Ik', 'Fi']
IMDB_FOLD_SCHEMA               = get_schema(IMDB_FOLD_SCHEMA_FIELDS)

IMDB_BIG_FOLD_SCHEMA_FIELDS    = ['Gi']
IMDB_BIG_FOLD_SCHEMA           = get_schema(IMDB_BIG_FOLD_SCHEMA_FIELDS)

# mrf.txt
WIKI_SCHEMA_FIELDS     = [ 'Gi', 'Ti', 'Rl' ]
WIKI_SCHEMA            = get_schema(WIKI_SCHEMA_FIELDS)

WIKT_MC_SCHEMA_FIELDS  = ['Gi', 'Ti', 'Ty', 'Og', 'Me', 'Ak', 'Ke', 'Fl', 'Dl', 'Wk', 'Pr']
WIKT_MC_SCHEMA         = get_schema(WIKT_MC_SCHEMA_FIELDS)

WIKI_MC_SCHEMA_FIELDS  =  ['Gi', 'Ti', 'Ds', 'Ty', 'De', 'Ak', 'Ik', 'Va', 'Ke', 'Kh',\
                           'Rd', 'Ws', 'Bd', 'Dd', 'Oc', 'Ps', 'Fl', 'Dl', 'Wk', 'Md']
WIKI_ENTERTAINMENT_SCHEMA_FIELDS    = ["Gi", "Ti", "Ak", "Ik", "Va", "Ll", "Pa", "Ci", "Vt", "Rr", "Iv", "Ge", "Cl", "Sy", "Di", "Pr", "Wr", "Er", "Ry", "Od", "Ho",\
                                        'Sn', 'En', 'Co', 'Oc', 'Oy',\
                                        'Pc', 'Np', 'Pp', 'De', 'Bd',\
                                        'Dd', 'Bp', 'Ps', 'Cc', 'Zc', 'Im',\
                                        'Zi', 'If', 'Sp', 'Ac', 'Ec', 'Cn',\
                                        'Ml', 'Wb', 'Uc', 'Ed', 'Mi', 'Pi', 'Rg', 'Sx', 'Fd', 'Uf', 'Oa', 'Fo', 'Ft', 'St', 'Du', 'Tp', 'Pn', 'Zl', 'Rp']
WIKI_ENTERTAINMENT_SCHEMA    = get_schema(WIKI_ENTERTAINMENT_SCHEMA_FIELDS)

#wikidata
WIKIDATA_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Ak', 'De', 'Vt', 'Sy', 'Ot',\
                           'Sp', 'Sx', 'Ig', 'Mi', 'Sn', 'En', 'Pn', 'Tp', 'Fd',\
                           'Ge', 'Ca', 'Du', 'Cl', 'Ml', 'Ll', 'Ry', 'Ec', 'Cn', 'Od',\
                           'Oy', 'Di', 'Wr', 'Co', 'Pr', 'Pc', 'Aw', 'Bd',\
                           'Dd', 'Oc', 'Im', 'Zc', 'Rp' ]

WIKIDATA_SCHEMA = get_schema(WIKIDATA_SCHEMA_FIELDS)

# sports data files
TOURNAMENT_MC_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ak', 'Za', 'Ke', 'Af', 'Sp', 'Sm', 'Ge', 'Is', 'Te', 'De', 'Ss', 'Se', 'Rd', 'Pi', 'Wi', 'Xt', 'Sx', 'Fd']
TOURNAMENT_MC_SCHEMA        = get_schema(TOURNAMENT_MC_SCHEMA_FIELDS)
TEAM_MC_SCHEMA_FIELDS       = [ 'Gi', 'Ti', 'Vt', 'Ak', 'Ik', 'Af', 'Sp', 'Sm', 'Ge', 'Is', 'Rt', 'Cs', 'Pi', 'Lo', 'Ip', 'Sk', 'Dt', 'Fd', 'Sx']
TEAM_MC_SCHEMA              = get_schema(TEAM_MC_SCHEMA_FIELDS)
PLAYER_MC_SCHEMA_FIELDS     = [ 'Gi', 'Ti', 'Ak', 'Af', 'Ro', 'Sp', 'Wt', 'Ht', 'Sa', 'Bu', 'De', 'Im', 'Bd', 'Pl', 'Vt', 'Is', 'Ge', 'Sk', 'Rt', 'Dt', 'Rl', 'Sx', 'Fd']
PLAYER_MC_SCHEMA            = get_schema(PLAYER_MC_SCHEMA_FIELDS)
PLAYER_FOLD_SCHEMA_FIELDS     = [ 'Gi', 'Ti', 'Vt', 'Fi' ]
PLAYER_FOLD_SCHEMA            = get_schema(PLAYER_FOLD_SCHEMA_FIELDS)
GAME_MC_SCHEMA_FIELDS       = [ 'Gi', 'Ti', 'Ep', 'Ps', 'Dt', 'Du', 'St', 'Lo', 'Ge', 'De', 'Af', 'Ch', 'Ht', 'Pi', 'Sr', 'Sc', 'Ts', 'Vt', 'Sp', 'Ev', 'Wi', 'Gp', 'Sm', 'Od', 'Tu']
GAME_MC_SCHEMA              = get_schema(GAME_MC_SCHEMA_FIELDS)
GROUP_MC_SCHEMA_FIELDS      = ['Gi', 'Ti', 'Xt', 'Pi', 'De', 'To', 'Vt', 'Ak', 'Ke', 'Ge', 'Sp']
GROUP_MC_SCHEMA              = get_schema(GROUP_MC_SCHEMA_FIELDS)
STADIUM_MC_SCHEMA_FIELDS      = ['Gi', 'Ti', 'Vt', 'Cl', 'St', 'Ct', 'Ak', 'Ke', 'Sp']
STADIUM_MC_SCHEMA              = get_schema(STADIUM_MC_SCHEMA_FIELDS)
REDIS_SPORTS_MC_FIELDS         = ['Gi', 'Md']
REDIS_SPORTS_MC_SCHEMA         = get_schema(REDIS_SPORTS_MC_FIELDS)

SPORTS_FOLD_SCHEMA_FIELDS     = [ 'Gi', 'Ti', 'Vt', 'De', 'Ke', 'Ge', 'Fi', 'Is', 'Sp', 'Ev', 'Pa' ]
SPORTS_FOLD_SCHEMA            = get_schema(SPORTS_FOLD_SCHEMA_FIELDS)
TEAM_FOLD_SCHEMA_FIELDS     = [ 'Gi', 'Ti', 'Vt', 'Fi' ]
TEAM_FOLD_SCHEMA            = get_schema(TEAM_FOLD_SCHEMA_FIELDS)
SPORTS_POP_SCHEMA_FIELDS     = [ 'Gi', 'Bp', 'Vt']
SPORTS_POP_SCHEMA            = get_schema(SPORTS_POP_SCHEMA_FIELDS)

SPORTS_TYPE_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Xt', 'Ak', 'Ke', 'Pi' ]
SPORTS_TYPE_SCHEMA = get_schema(SPORTS_TYPE_SCHEMA_FIELDS)

#Awards datagen
AWARD_MC_SCHEMA_FIELDS      = ['Gi', 'Vt', 'Xt', 'Ti', 'Ak', 'Nc', 'Pi']
AWARD_MC_SCHEMA      = get_schema(AWARD_MC_SCHEMA_FIELDS)

AWARD_HISTORY_FIELDS = [ 'Sk', 'Nc', 'Ca', 'Da', 'Ce', 'Wn', 'Wo', 'Ge', 'Wi', 'Vt', 'Xt' ]
AWARD_HISTORY_SCHEMA = get_schema(AWARD_HISTORY_FIELDS)

AWARD_GIDS_FIELDS    = ['Ai', 'Gi']
AWARD_GIDS_SCHEMA    = get_schema(AWARD_GIDS_FIELDS)

IMDB_AWARDS_FIELDS   = ['Tt', 'Ev', 'Cr', 'Wn', 'Ac']
IMDB_AWARDS_SCHEMA   = get_schema(IMDB_AWARDS_FIELDS)

# Music data files
MUSIC_LASTFM_MC_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Sk', 'Vt', 'Ge', 'Pp', 'De', 'Im', 'Bm', 'Al', ]
MUSIC_LASTFM_MC_SCHEMA = get_schema(MUSIC_LASTFM_MC_SCHEMA_FIELDS)

MUSIC_LASTFM_MC_NEW_SCHEMA_FIELDS = MUSIC_LASTFM_MC_SCHEMA_FIELDS + ['Dc', 'Ak']
MUSIC_LASTFM_MC_NEW_SCHEMA = get_schema(MUSIC_LASTFM_MC_NEW_SCHEMA_FIELDS)

MUSIC_LASTFM_ARTIST_LINKS_FIELDS = ['Gi', 'Ti', 'Ur']
MUSIC_LASTFM_ARTIST_LINKS_SCHEMA = get_schema(MUSIC_LASTFM_ARTIST_LINKS_FIELDS)

MUSIC_SERVER_MC_SCHEMA_FIELDS = MUSIC_LASTFM_MC_SCHEMA_FIELDS + [ 'Ry', 'Ig', 'Wr', 'Co', 'Ak', 'Rd' ]
MUSIC_SERVER_MC_SCHEMA = get_schema(MUSIC_SERVER_MC_SCHEMA_FIELDS)

MUSIC_SERVER_MC_NEW_SCHEMA_FIELDS = MUSIC_LASTFM_MC_NEW_SCHEMA_FIELDS + [ 'Ry', 'Ig', 'Wr', 'Co', 'Rd' ]
MUSIC_SERVER_MC_NEW_SCHEMA = get_schema(MUSIC_SERVER_MC_NEW_SCHEMA_FIELDS)

MUSIC_SEED_ALBUM_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ry', 'Ge', 'Gg', 'Pp', 'Wr', 'Co', 'Od', 'Tg', 'Nv', 'Im',
                                   'Rd', 'Cp', 'Dc', 'Fd', 'De', 'Xt', 'Ad', 'Md', 'In']
MUSIC_SEED_ALBUM_SCHEMA = get_schema(MUSIC_SEED_ALBUM_SCHEMA_FIELDS)

CUR_MUSIC_SEED_ALBUM_SCHEMA_FIELDS = copy(MUSIC_SEED_ALBUM_SCHEMA_FIELDS)
CUR_MUSIC_SEED_ALBUM_SCHEMA_FIELDS.append('Cr')
CUR_MUSIC_SEED_ALBUM_SCHEMA = get_schema(CUR_MUSIC_SEED_ALBUM_SCHEMA_FIELDS)

MUSIC_SEED_ARTIST_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ak', 'Bd', 'Br', 'Dd', 'Sx', 'Bm', 'Xt', 'Ip', 'Ge', 'Gg',
                                    'Ds', 'Da', 'Ac', 'Nv', 'De', 'Im', 'Rd', 'Dc', 'Fd', 'Pp', 'Tg', 'Db' ]
MUSIC_SEED_ARTIST_SCHEMA = get_schema(MUSIC_SEED_ARTIST_SCHEMA_FIELDS)

MUSIC_SEED_TRACK_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Pp', 'Wr', 'Co', 'Al', 'Rd', 'Pr', 'Rc', 'Du', 'Tg', 'Cp',
                                   'Dc', 'Ge', 'Fd', 'So', 'In', 'Th', 'Tn' ]
MUSIC_SEED_TRACK_SCHEMA = get_schema(MUSIC_SEED_TRACK_SCHEMA_FIELDS)

CUR_MUSIC_SEED_TRACK_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Pp', 'Wr', 'Co', 'Al', 'Rd', 'Pr', 'Rc', 'Du', 'Tg', 'Cp',
                                       'Dc', 'Ge', 'Fd', 'Da', 'So', 'Zc' ]
CUR_MUSIC_SEED_TRACK_SCHEMA = get_schema(CUR_MUSIC_SEED_TRACK_SCHEMA_FIELDS)

MUSIC_SEED_SONG_FOLD_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Sk', 'Pp', 'Al',
    'Wr', 'Pr', 'Co', 'Vt', 'Nv', 'Cc', 'Tg', 'Ry', 'In', 'Ge', 'Tr', 'Bt', 'Th', 'Tn' ]
MUSIC_SEED_SONG_FOLD_SCHEMA = get_schema(MUSIC_SEED_SONG_FOLD_SCHEMA_FIELDS)

MUSIC_SEED_COMPOSITION_FOLD_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Sk', 'Co', 'Vt', 'Tg', 'So', 'Pp' ]
MUSIC_SEED_COMPOSITION_FOLD_SCHEMA = get_schema(MUSIC_SEED_COMPOSITION_FOLD_SCHEMA_FIELDS)

MUSIC_SEED_LEXICAL_FOLD_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Sk', 'Vt', 'Nv', 'Cc' ]
MUSIC_SEED_LEXICAL_FOLD_SCHEMA = get_schema(MUSIC_SEED_LEXICAL_FOLD_SCHEMA_FIELDS)

MUSIC_SEED_FOLD_SCHEMA_FIELDS = [ 'Gi', 'Ti', 'Ak', 'Ry', 'Ig', 'Vt', 'Xt', 'Wt', 'Tg' ]
MUSIC_SEED_FOLD_SCHEMA = get_schema(MUSIC_SEED_FOLD_SCHEMA_FIELDS)

MUSIC_POP_SCHEMA_FIELDS = ['Gi', 'Ti', 'Ty', 'Bp']
MUSIC_POP_SCHEMA = get_schema(MUSIC_POP_SCHEMA_FIELDS)

MUSIC_POP_SCHEMA_WITH_ID_SPACE = copy(MUSIC_POP_SCHEMA)
MUSIC_POP_SCHEMA_WITH_ID_SPACE["Id"] = len(MUSIC_POP_SCHEMA_WITH_ID_SPACE)

YTMUSIC_POP_SCHEMA_FIELDS = ['Gi', 'Ti', 'Ty', 'Bp', 'Bc']
YTMUSIC_POP_SCHEMA = get_schema(YTMUSIC_POP_SCHEMA_FIELDS)

MUSIC_FOLD_SCHEMA_FIELDS = ['Gi', 'Ti', 'Ty', 'Fi', 'Sk']
MUSIC_FOLD_SCHEMA = get_schema(MUSIC_FOLD_SCHEMA_FIELDS)

MUSIC_BIG_FOLD_SCHEMA_FIELDS = ['Gi', 'Ti', 'Ty']
MUSIC_BIG_FOLD_SCHEMA = get_schema(MUSIC_BIG_FOLD_SCHEMA_FIELDS)

MUSIC_LASTFM_RECOMMENDATION_SCHEMA_FIELDS = ['Gi', 'Ti', 'Rl', 'Vt', 'Xt']
MUSIC_LASTFM_RECOMMENDATION_SCHEMA = get_schema(MUSIC_LASTFM_RECOMMENDATION_SCHEMA_FIELDS)

# Used in new_edb_rule.out, new_music_rule.out, new_ct_rule.out
RULE_SCHEMA_FIELDS     = [ 'Gi', 'Og', 'Ti', 'Ty', 'Rl', 'Ll', 'Kr', 'Th']
RULE_SCHEMA            = get_schema(RULE_SCHEMA_FIELDS)

SPORTS_SCHEMA_FIELDS   = [ 'Gi', 'Ty', 'Ti', 'Th', 'Rl', 'Ru', 'Rs', 'R1' ]
SPORTS_SCHEMA          = get_schema(SPORTS_SCHEMA_FIELDS)

CONCEPTS_SCHEMA_FIELDS = ['Gi', 'Ti', 'Vt', 'Xt', 'Rl', 'De', 'Ke', 'Bs', 'Th']
CONCEPTS_SCHEMA        = get_schema(CONCEPTS_SCHEMA_FIELDS)
CONTENT_TYPE_SCHEMA_FIELDS  = ['Gi', 'Ti', 'Vt', 'Xt', 'Bs', 'Zl']
CONTENT_TYPE_SCHEMA    = get_schema(CONTENT_TYPE_SCHEMA_FIELDS)
CONTENT_SCHEMA_FIELDS  = ['Gi', 'Vt', 'Xt', 'Mi', 'Ti', 'Va', 'Ak', 'Ik', 'Ep', 'Ae', 'Bs']
CONTENT_SCHEMA         = get_schema(CONTENT_SCHEMA_FIELDS)

POP_SCHEMA_FIELDS      = [ 'Gi', 'Ty', 'Bp', 'Ti' ]
POP_SCHEMA             = get_schema(POP_SCHEMA_FIELDS)

PHRASE_SCHEMA_FIELDS   = [ 'Ti', 'Bp', 'Ty', 'Ir', 'Wt', 'Df' ]
PHRASE_SCHEMA          = get_schema(PHRASE_SCHEMA_FIELDS)

MGSTR_SCHEMA_FIELDS    = [ 'Ti', 'Re' ]
MGSTR_SCHEMA           = get_schema(MGSTR_SCHEMA_FIELDS)

MGGIDS_SCHEMA_FIELDS   = [ 'Gi', 'Ti', 'Vi' ]
MGGIDS_SCHEMA          = get_schema(MGGIDS_SCHEMA_FIELDS)

# MISC KG Fields

DECADE_MC_SCHEMA_FIELDS   = [ 'Gi', 'Vt', 'Ti', 'Ak', 'Ry']
DECADE_MC_SCHEMA          = get_schema(DECADE_MC_SCHEMA_FIELDS)

DETAIL_MC_SCHEMA_FIELDS   = [ 'Gi', 'Vt', 'Ti', 'Ak', 'Rs', 'Xt']
DETAIL_MC_SCHEMA          = get_schema(DETAIL_MC_SCHEMA_FIELDS)

LANGUAGE_MC_SCHEMA_FIELDS = [ 'Gi', 'Vt', 'Ti', 'Ak', 'Cl', 'Bp', 'Zi', 'Pi' ]
LANGUAGE_MC_SCHEMA        = get_schema(LANGUAGE_MC_SCHEMA_FIELDS)

REGION_MC_SCHEMA_FIELDS   = [ 'Gi', 'Vt', 'Ti', 'Ak', 'Cl', 'Bp', 'Zi', 'Xt', 'Pi']
REGION_MC_SCHEMA        = get_schema(REGION_MC_SCHEMA_FIELDS)

MISC_ENTITIES_SCHEMA_FIELDS   = [ 'Gi', 'Vt', 'Ke' ]
MISC_ENTITIES_SCHEMA          = get_schema(MISC_ENTITIES_SCHEMA_FIELDS)

RATING_MC_SCHEMA_FIELDS   = [ 'Gi', 'Vt', 'Xt', 'Ti', 'Ak', 'Rk', 'Cl', 'Rg', 'Rv' ]
RATING_MC_SCHEMA          = get_schema(RATING_MC_SCHEMA_FIELDS)

FILTER_MC_SCHEMA_FIELDS   = [ 'Gi', 'Vt', 'Xt', 'Ti', 'Ak', 'Tg', 'At']
FILTER_MC_SCHEMA          = get_schema(FILTER_MC_SCHEMA_FIELDS)

QUOTES_MC_SCHEMA_FIELDS    = ['Gi', 'Ti', 'Aq' ]
QUOTES_MC_SCHEMA           = get_schema(QUOTES_MC_SCHEMA_FIELDS)

IPC_MC_SCHEMA_FILEDS      = ['Gi', 'Vt', 'Ti']
IPC_MC_SCHEMA             = get_schema(IPC_MC_SCHEMA_FILEDS)

GRAMMAR_MC_FIELDS         = [ 'Gi', 'Vt', 'Xt', 'Ti', 'Ml', 'Ak', 'Ke' ]
GRAMMAR_MC_SCHEMA         = get_schema(GRAMMAR_MC_FIELDS)

CHARMAP_MC_FIELDS         = [ 'Gi', 'Vt', 'Ti', 'Ml', 'Vi', 'St', 'Sp', 'Ig' ]
CHARMAP_MC_SCHEMA         = get_schema(CHARMAP_MC_FIELDS)

WORDMAP_MC_FIELDS         = [ 'Gi', 'Vt', 'Ti', 'Ml', 'Vi', 'St', 'Sp', 'Ig' ]
WORDMAP_MC_SCHEMA         = get_schema(WORDMAP_MC_FIELDS)

GENRE_MC_SCHEMA_FIELDS    = [ 'Gi', 'Ti', 'Vt', 'Xt', 'Ak', 'Tg', 'Bp', 'An', 'Pi', 'Mp', 'Um']
GENRE_MC_SCHEMA           = get_schema(GENRE_MC_SCHEMA_FIELDS)

GENRES_FIELDS             = [ 'Gi', 'Ti', 'Vt', 'Tg', 'Bp', 'An' ]
GENRES_SCHEMA             = get_schema(GENRES_FIELDS)

# TV SEED SCHEMA
# fold.data.gen.merge
TV_SEED_FOLD_SCHEMA_FIELDS     = ['Gi', 'Ti', 'Vt', 'Ge', 'Ak', 'Ik', 'Va', 'Ke', 'Rd', 'Im', 'Tg', 'Np', 'Rl', 'Te', 'To', 'Tl', 'Bs', 'Xt', 'Ca', 'Sp', 'Bd', 'Sx', 'Do', 'Ro', 'Fd', 'De', 'Zl', 'Cl', 'St', 'Ct', 'Ry', 'Pa', 'Pi', 'Aw', 'Rt', 'Dt', 'Sm', 'Dd', 'Dl']
TV_SEED_FOLD_SCHEMA            = get_schema(TV_SEED_FOLD_SCHEMA_FIELDS)

TV_ARCHIVE_FOLD_SCHEMA_FIELDS  = TV_SEED_FOLD_SCHEMA_FIELDS[:]
TV_ARCHIVE_FOLD_SCHEMA         = get_schema(TV_ARCHIVE_FOLD_SCHEMA_FIELDS)

# role.data.gen.merge
TV_ARCHIVE_ROLE_SCHEMA_FIELDS  = ['Gi', 'Ti', 'Vt', 'Ge', 'Ak', 'Ik', 'Va', 'Ke', 'Rd', 'Pa', 'Tg', 'Oc', 'Cg']
TV_ARCHIVE_ROLE_SCHEMA         = get_schema(TV_ARCHIVE_ROLE_SCHEMA_FIELDS)

TV_SEED_PROGRAMS_COMMON_FIELDS = ['Gi', 'Ti', 'Vt', 'Ge', 'Gg', 'Rd', 'Ak', 'Ik', 'Va', 'Ic', 'Ca', 'Ro', 'Di', 'Pr', 'Wr', 'Co', 'Ry', 'Od', 'Cl', 'Ll', 'Ig', 'In', 'Ke', 'Fd', 'Sd', 'De', 'Ra', 'Im', 'Du', 'Tg', 'Aw', 'Uc', 'Rl', 'Tl', 'Oa', 'Ol', 'Oe', 'Pc', 'Zl', 'Pa']

# seed igs
SEED_IGS_SCHEMA_FIELDS         = ['Gi', 'Ti', 'Ig', 'In']

# movie.data.gen.merge
TV_ARCHIVE_MOVIE_SCHEMA_FIELDS = TV_SEED_PROGRAMS_COMMON_FIELDS[:]
TV_ARCHIVE_MOVIE_SCHEMA_FIELDS.extend(('Ng', 'Gk', 'Sq'))
TV_ARCHIVE_MOVIE_SCHEMA        = get_schema(TV_ARCHIVE_MOVIE_SCHEMA_FIELDS)

# tvvideo.data.gen.merge
TV_SEED_TVVIDEO_SCHEMA_FIELDS     = TV_SEED_PROGRAMS_COMMON_FIELDS[:]
TV_SEED_TVVIDEO_SCHEMA_FIELDS.extend(('Gk', 'Sq'))
TV_SEED_TVVIDEO_SCHEMA            = get_schema(TV_SEED_TVVIDEO_SCHEMA_FIELDS)
TV_ARCHIVE_TVVIDEO_SCHEMA_FIELDS  = TV_SEED_PROGRAMS_COMMON_FIELDS[:]
TV_ARCHIVE_TVVIDEO_SCHEMA_FIELDS.extend(('Gk', 'Sq'))
TV_ARCHIVE_TVVIDEO_SCHEMA         = get_schema(TV_ARCHIVE_TVVIDEO_SCHEMA_FIELDS)

# tvseries.data.gen.merge
TV_ARCHIVE_TVSERIES_SCHEMA_FIELDS = TV_SEED_PROGRAMS_COMMON_FIELDS[:]
TV_ARCHIVE_TVSERIES_SCHEMA_FIELDS.extend(('Ho', 'Np', 'Gk',))
TV_ARCHIVE_TVSERIES_SCHEMA        = get_schema(TV_ARCHIVE_TVSERIES_SCHEMA_FIELDS)

# episode.data.gen.merge
TV_ARCHIVE_EPISODE_SCHEMA_FIELDS  = TV_SEED_PROGRAMS_COMMON_FIELDS[:]
TV_ARCHIVE_EPISODE_SCHEMA_FIELDS.extend(('Ep', 'Pi', 'Sn', 'En', 'Ae'))
TV_ARCHIVE_EPISODE_SCHEMA         = get_schema(TV_ARCHIVE_EPISODE_SCHEMA_FIELDS)

ROVI_CHANNEL_MC_SCHEMA_FIELDS = ['Gi', 'Ti', 'Vt', 'Xt', 'Sk', 'Ak', 'Pi', 'Ik', 'Af', 'Bp', 'Cs', 'Im', 'Cl', 'St', 'Ct', 'Ge', 'Ll', 'Tg', 'Nv', 'Is', 'Sc', 'Ow', 'Rg', 'Ng', 'Og', 'Sl', 'Ag', 'Fd', 'Tz']
ROVI_CHANNEL_MC_SCHEMA =  get_schema(ROVI_CHANNEL_MC_SCHEMA_FIELDS)

ROVI_CHANFOLD_SCHEMA_FIELDS      = ['Gi', 'Ti', 'Vt', 'Af', 'Ak', 'Ke', 'Bp', 'Dp', 'Im', 'Tg', 'Ow', 'Xt', 'Pi', 'Fi', 'Fd']
ROVI_CHANFOLD_SCHEMA             = get_schema(ROVI_CHANFOLD_SCHEMA_FIELDS)

ROVI_AFF_SCHEMA_FIELDS      = ['Gi', 'Ti', 'Vt', 'Af', 'Ak', 'Ke', 'Bp', 'Dp', 'Im', 'Tg', 'Ow', 'Xt', 'Pi', 'Fi', 'Fd']
ROVI_AFF_SCHEMA             = get_schema(ROVI_AFF_SCHEMA_FIELDS)

# channel.data.gen.merge
TV_ARCHIVE_CHANNEL_SCHEMA_FIELDS  = ['Gi', 'Ti', 'Vt', 'Ak', 'Ik', 'Pi', 'Af', 'Cs', 'Im', 'Ge', 'Ll', 'Tg', 'Nv', 'Is', 'Sm', 'Ow']
TV_ARCHIVE_CHANNEL_SCHEMA         = get_schema(TV_ARCHIVE_CHANNEL_SCHEMA_FIELDS)

# chanfold.data.gen.merge
TV_ARCHIVE_CHANFOLD_SCHEMA_FIELDS   = ['Gi', 'Ti', 'Vt', 'Af', 'Im', 'Ak', 'Dp', 'Tg', 'Ow']
TV_ARCHIVE_CHANFOLD_SCHEMA          = get_schema(TV_ARCHIVE_CHANFOLD_SCHEMA_FIELDS)

TV_SEED_POPULARITY_FIELDS           = ['Gi', 'Bp', 'Ty']
TV_SEED_POPULARITY_SCHEMA           = get_schema(TV_SEED_POPULARITY_FIELDS)

TV_SEED_SEQUEL_FILE_FIELDS          = ['Gi', 'Ti', 'Ty', 'De', 'Ik', 'Fi', 'Wg']
TV_SEED_SEQUEL_FILE_SCHEMA          = get_schema(TV_SEED_SEQUEL_FILE_FIELDS)

TV_SEED_GENRE_FILE_FIELDS           = ['Gi', 'Ge', 'Gg', 'So']
TV_SEED_GENRE_FILE_SCHEMA           = get_schema(TV_SEED_GENRE_FILE_FIELDS)

TV_SEED_GENRE_MC_SCHEMA_FIELDS      = [ 'Gi', 'Ti', 'Ak', 'Vt', 'Tg', 'Np', 'Xt', 'Fd', 'Pi', 'Mp', 'Um' ]
TV_SEED_GENRE_MC_SCHEMA             = get_schema(TV_SEED_GENRE_MC_SCHEMA_FIELDS)

TV_SEED_RATING_FILE_FIELDS           = ['Gi', 'Ra', 'So']
TV_SEED_RATING_FILE_SCHEMA           = get_schema(TV_SEED_RATING_FILE_FIELDS)

TV_SEED_RATING_MC_FILE_FIELDS           = ['Gi', 'Ti', 'Vt', 'Xt', 'Zl', 'Rk', 'Cl', 'Rv', 'Ak']
TV_SEED_RATING_MC_FILE_SCHEMA           = get_schema(TV_SEED_RATING_MC_FILE_FIELDS)

TV_SEED_GID_LIST_FIELDS                 = ['Gi', 'Vt']
TV_SEED_GID_LIST_SCHEMA                 = get_schema(TV_SEED_GID_LIST_FIELDS)

TV_SEED_RATING_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Cl', 'Rg', 'Rk', 'Rv', 'Va', 'Zl', 'Ak', 'Xt']
TV_SEED_RATING_SCHEMA                   = get_schema(TV_SEED_RATING_SCHEMA_FIELDS)

TV_SEED_LANGUAGE_SCHEMA_FIELDS          = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Ol', 'Ik', 'Im', 'Ke', 'Va', 'Zl']
TV_SEED_LANGUAGE_SCHEMA                 = get_schema(TV_SEED_LANGUAGE_SCHEMA_FIELDS)

TV_SEED_GENRE_SCHEMA_FIELDS             = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Do', 'Fd', 'Gk', 'Ik', 'Im', 'Ke', 'Ol', 'Mp', 'Np', 'Od', 'Pi', 'Pc', 'Ry', 'Tg', 'Um', 'Va', 'Xt', 'Zl']
TV_SEED_GENRE_SCHEMA                    = get_schema(TV_SEED_GENRE_SCHEMA_FIELDS)

TV_SEED_FILTER_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Ak', 'Tg', 'Va', 'Xt', 'Zl']
TV_SEED_FILTER_SCHEMA                   = get_schema(TV_SEED_FILTER_SCHEMA_FIELDS)

TV_SEED_DECADE_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Ak', 'Od', 'Ry', 'Zl']
TV_SEED_DECADE_SCHEMA                   = get_schema(TV_SEED_DECADE_SCHEMA_FIELDS)

TV_SEED_SPORT_SCHEMA_FIELDS             = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Ik', 'Im', 'Ol', 'Ke', 'Pi', 'Va', 'Zl']
TV_SEED_SPORT_SCHEMA                    = get_schema(TV_SEED_SPORT_SCHEMA_FIELDS)

TV_SEED_TOURNAMENT_SCHEMA_FIELDS        = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Fd', 'Ge', 'Ik', 'Im', 'Ol', 'Ke', 'Ll', 'Od', 'Rd', 'Ry', 'Sp', 'Tg', 'To', 'Va', 'Xt', 'Zl', 'Ig', 'Pi']
TV_SEED_TOURNAMENT_SCHEMA               = get_schema(TV_SEED_TOURNAMENT_SCHEMA_FIELDS)

TV_SEED_TEAM_SCHEMA_FIELDS              = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Do', 'Ge', 'Ik', 'Im', 'Ol', 'Ke', 'Ll', 'Sp', 'Tg', 'To', 'Va', 'Zl', 'Ig', 'Xt']
TV_SEED_TEAM_SCHEMA                     = get_schema(TV_SEED_TEAM_SCHEMA_FIELDS)

TV_SEED_SPORTS_GROUP_SCHEMA_FIELDS      = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Ik', 'Im', 'Ol', 'Ke', 'Sp', 'Tg', 'To', 'Va', 'Zl', 'Fd', 'Xt']
TV_SEED_SPORTS_GROUP_SCHEMA             = get_schema(TV_SEED_SPORTS_GROUP_SCHEMA_FIELDS)

TV_SEED_STADIUM_SCHEMA_FIELDS           = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Ct', 'Ik', 'Im', 'Ol', 'Ke', 'St', 'Va', 'Zl']
TV_SEED_STADIUM_SCHEMA                  = get_schema(TV_SEED_STADIUM_SCHEMA_FIELDS)

TV_SEED_PHRASE_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Ak', 'Aw', 'Cl', 'De', 'Do', 'Fd', 'Gk', 'Ik', 'Im', 'Pc', 'Ac', 'Ol', 'Ke', 'Ll', 'Od', 'Rd', 'Ry', 'Sq', 'Tl', 'Va', 'Xt', 'Zl']
TV_SEED_PHRASE_SCHEMA                   = get_schema(TV_SEED_PHRASE_SCHEMA_FIELDS)

TV_SEED_AWARD_SCHEMA_FIELDS             = ['Gi', 'Ti', 'Vt', 'Ak', 'Cl', 'Ik', 'Im', 'Ke', 'Ol', 'Nc', 'Pi', 'Ac', 'Va', 'Xt', 'Zl']
TV_SEED_AWARD_SCHEMA                    = get_schema(TV_SEED_AWARD_SCHEMA_FIELDS)

TV_SEED_PERSON_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Ak', 'Bd', 'Bs', 'Cl', 'De', 'Do', 'En', 'Fd', 'Ge', 'Gk', 'Pc', 'Ac', 'Ol', 'Ik', 'Im', 'Ke', 'Ll', 'Od', 'Pi', 'Rd', 'Ro', 'Ry', 'Sn', 'Sp', 'Sx', 'Te', 'Tg', 'Tl', 'To', 'Va', 'Xt', 'Zl', 'Ig', 'Aw']
TV_SEED_PERSON_SCHEMA                   = get_schema(TV_SEED_PERSON_SCHEMA_FIELDS)

TV_SEED_MOVIE_SCHEMA_FIELDS             = ['Gi', 'Ti', 'Vt', 'Ak', 'Aw', 'Ca', 'Cl', 'Co', 'De', 'Di', 'Dl', 'Do', 'Du', 'En', 'Fd', 'Ge', 'Gg', 'Gk', 'Ho', 'Ic', 'Ig', 'Im', 'Ke', 'Ll', 'Ol', 'Oa', 'Od', 'Ae', 'Pc', 'Ac', 'Pi', 'Pr', 'Ra', 'Rd', 'Rl', 'Ro', 'Ry', 'Sn', 'Sq', 'Tl', 'Va', 'Wr', 'Xt', 'Zc', 'Zl', 'Pa']
TV_SEED_MOVIE_SCHEMA                    = get_schema(TV_SEED_MOVIE_SCHEMA_FIELDS)

TV_SEED_TVSERIES_SCHEMA_FIELDS          = ['Gi', 'Ti', 'Vt', 'Ak', 'Aw', 'Ca', 'Cl', 'Co', 'De', 'Di', 'Do', 'Du', 'En', 'Fd', 'Ge', 'Gg', 'Gk', 'Ho', 'Ic', 'Ig', 'Ik', 'Im', 'Ke', 'Ll', 'Np', 'Ol', 'Oa', 'Od', 'Ae', 'Pc', 'Ac', 'Pi', 'Pr', 'Ra', 'Rd', 'Rl', 'Ro', 'Ry', 'Sn', 'Sq', 'Tl', 'Va', 'Wr', 'Xt', 'Zc', 'Zl', 'Pa']
TV_SEED_TVSERIES_SCHEMA                 = get_schema(TV_SEED_TVSERIES_SCHEMA_FIELDS)

TV_SEED_EPISODE_SCHEMA_FIELDS           = ['Gi', 'Ti', 'Vt', 'Ak', 'Aw', 'Ca', 'Cl', 'Co', 'De', 'Di', 'Du', 'En', 'Ep', 'Fd', 'Ge', 'Gg', 'Gk', 'Ho', 'Ic', 'Ig', 'Ik', 'Im', 'Ke', 'Ll', 'Ol', 'Oa', 'Od', 'Oe', 'Ae', 'Pc', 'Ac', 'Pi', 'Pr', 'Ra', 'Rd', 'Rl', 'Ro', 'Ry', 'Sn', 'Sq', 'Tg', 'Tl', 'Va', 'Wr', 'Xt', 'Zc', 'Zl', 'Pa', 'Mi']
TV_SEED_EPISODE_SCHEMA                  = get_schema(TV_SEED_EPISODE_SCHEMA_FIELDS)

TV_SEED_SEQUEL_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Ak', 'Ca', 'De', 'Fi', 'Ge', 'Ik', 'Im', 'Ke', 'Np', 'Pa', 'Rd', 'Rl', 'Ro', 'Tg', 'Va', 'Wg', 'Xt', 'Zl']
TV_SEED_SEQUEL_SCHEMA                   = get_schema(TV_SEED_SEQUEL_SCHEMA_FIELDS)

TV_SEED_ROLE_SCHEMA_FIELDS              = ['Gi', 'Ti', 'Vt', 'Ge', 'Ak', 'Ik', 'Va', 'Ke', 'Rd', 'Pa', 'Tg', 'Oc', 'Cg']
TV_SEED_ROLE_SCHEMA                     = get_schema(TV_SEED_ROLE_SCHEMA_FIELDS)

TV_SEED_CHANNEL_SCHEMA_FIELDS           = ['Gi', 'Ti', 'Vt', 'Ak', 'Ik', 'Pi', 'Af', 'Cs', 'Im', 'Ge', 'Ll', 'Tg', 'Nv', 'Is', 'Sm', 'Ow', 'Zl', 'Xt']
TV_SEED_CHANNEL_SCHEMA                  = get_schema(TV_SEED_CHANNEL_SCHEMA_FIELDS)

TV_SEED_CHANFOLD_SCHEMA_FIELDS          = ['Gi', 'Ti', 'Vt', 'Af', 'Im', 'Ak', 'Dp', 'Tg', 'Ow', 'Zl', 'Fi', 'Xt']
TV_SEED_CHANFOLD_SCHEMA                 = get_schema(TV_SEED_CHANFOLD_SCHEMA_FIELDS)

TV_SEED_REGION_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Vt', 'Ak', 'Ik', 'Im', 'Ke', 'Ol', 'Oa', 'Va', 'Ll', 'Cl', 'Xt', 'Zl']
TV_SEED_REGION_SCHEMA                   = get_schema(TV_SEED_REGION_SCHEMA_FIELDS)

TV_SEED_PC_SCHEMA_FIELDS                = ['Gi', 'Ti', 'Vt', 'Va', 'Zl']
TV_SEED_PC_SCHEMA                       = get_schema(TV_SEED_PC_SCHEMA_FIELDS)

TV_SEED_OAC_SCHEMA_FIELDS               = ['Gi', 'Ti', 'Vt', 'Va', 'Zl']
TV_SEED_OAC_SCHEMA                      = get_schema(TV_SEED_OAC_SCHEMA_FIELDS)

TV_SEED_TYPE_TO_SCHEMA                  = {
    CONTENT_TYPE_RATING: TV_SEED_RATING_SCHEMA_FIELDS,
    CONTENT_TYPE_LANGUAGE: TV_SEED_LANGUAGE_SCHEMA_FIELDS,
    CONTENT_TYPE_GENRE: TV_SEED_GENRE_SCHEMA_FIELDS,
    CONTENT_TYPE_FILTER: TV_SEED_FILTER_SCHEMA_FIELDS,
    CONTENT_TYPE_DECADE: TV_SEED_DECADE_SCHEMA_FIELDS,
    CONTENT_TYPE_SPORT: TV_SEED_SPORT_SCHEMA_FIELDS,
    CONTENT_TYPE_TOURNAMENT: TV_SEED_TOURNAMENT_SCHEMA_FIELDS,
    CONTENT_TYPE_TEAM: TV_SEED_TEAM_SCHEMA_FIELDS,
    CONTENT_TYPE_SPORTS_GROUP: TV_SEED_SPORTS_GROUP_SCHEMA_FIELDS,
    CONTENT_TYPE_STADIUM: TV_SEED_STADIUM_SCHEMA_FIELDS,
    CONTENT_TYPE_PHRASE: TV_SEED_PHRASE_SCHEMA_FIELDS,
    CONTENT_TYPE_AWARD: TV_SEED_AWARD_SCHEMA_FIELDS,
    CONTENT_TYPE_PERSON: TV_SEED_PERSON_SCHEMA_FIELDS,
    CONTENT_TYPE_MOVIE: TV_SEED_MOVIE_SCHEMA_FIELDS,
    CONTENT_TYPE_TVSERIES: TV_SEED_TVSERIES_SCHEMA_FIELDS,
    CONTENT_TYPE_TVVIDEO: TV_SEED_TVVIDEO_SCHEMA_FIELDS,
    CONTENT_TYPE_EPISODE: TV_SEED_EPISODE_SCHEMA_FIELDS,
    CONTENT_TYPE_SEQUEL: TV_SEED_SEQUEL_SCHEMA_FIELDS,
    CONTENT_TYPE_ROLE: TV_SEED_ROLE_SCHEMA_FIELDS,
    CONTENT_TYPE_CHANNEL: TV_SEED_CHANNEL_SCHEMA_FIELDS,
    CONTENT_TYPE_CHANNEL_AFFILIATION: TV_SEED_CHANFOLD_SCHEMA_FIELDS,
    CONTENT_TYPE_REGION: TV_SEED_REGION_SCHEMA_FIELDS,
    CONTENT_TYPE_PC: TV_SEED_PC_SCHEMA_FIELDS,
    CONTENT_TYPE_OAC: TV_SEED_OAC_SCHEMA_FIELDS
}

TV_SEED_POP_FILE_FIELDS             = ['Gi', 'Bp', 'Ty']
TV_SEED_POP_FILE_SCHEMA             = get_schema(TV_SEED_POP_FILE_FIELDS)

TV_SEED_MERGE_FILE_FIELDS             = ['Gi', 'Sk', 'Pi']
TV_SEED_MERGE_FILE_SCHEMA             = get_schema(TV_SEED_MERGE_FILE_FIELDS)

TV_SEED_GID_FIELDS                  = ['Te', 'To', 'Pi', 'Cg']
TV_SEED_TITLE_GID_FIELDS            = ['Ca', 'Ic', 'Di', 'Pr', 'Ho', 'Wr', 'Ig', 'Rl', 'Aw', 'In']

TV_SEED_RECOMMENDATION_FILE_FIELDS  = ['Gi', 'Ti', 'Rl', 'Ty', 'Xt', 'Sc']
TV_SEED_RECOMMENDATION_FILE_SCHEMA  = get_schema(TV_SEED_RECOMMENDATION_FILE_FIELDS)

TV_SEED_IGS_FILE_FIELDS             = ['Gi', 'Ti', 'Ig', 'In', 'So']
TV_SEED_IGS_FILE_SCHEMA             = get_schema(TV_SEED_IGS_FILE_FIELDS)

SEED_CREW_FIELDS                    = ['Gi', 'Vt', 'So', 'Pa',
                                       'Di', 'Pr', 'Ho', 'Co',
                                       'Wr', 'Uc', 'Ic', 'Zc']
SEED_CREW_SCHEMA                    = get_schema(SEED_CREW_FIELDS)

SEQUELS_FIELDS                      = ['Gi', 'Ti', 'Vt', 'Ak', 'Ke', 'Fi', 'Xt', 'So', 'Pi']
SEQUELS_SCHEMA                      = get_schema(SEQUELS_FIELDS)

# ROVI SCHEMA
ROVI_PROGRAM_FIELDS                 = ['Gi', 'Sk', 'Ti', 'Ak', 'Ep',
                                       'Ol', 'Oa', 'Oe',
                                       'Vt', 'Xt', 'Ot', 'Ry', 'Ll', 'Mi', 'Du',
                                       'Sn', 'En', 'Se', 'Di', 'Pr',
                                       'Ho', 'Ge', 'De', 'Od', 'Gd',
                                       'Ae', 'Ke', 'Ro', 'Rd', 'Tg',
                                       'Cs', 'Fd', 'Tl', 'Ht', 'Ud',
                                       'Te', 'Gs', 'Af', 'Ra', 'Ng', 'Zc',
                                       'Zg', 'Pc', 'Tn', 'Zl', 'Tp', 'Pn', 'Pa', 'Cl', 'Oy', 'Bp', 'Sy']
ROVI_PROGRAM_SCHEMA                 = get_schema(ROVI_PROGRAM_FIELDS)

ROVI_LANG_FIELDS                    = ["Gi", "Zl", "Ti", "Ak", "Ke",
                                       "Ca", "Di", "Pr", "Ho", "Zc",
                                       "De", "Ge", "Vt", "Zg", 'Fd',
                                       "Ep", 'Xt', 'Mi', 'Ry', 'Ll',
                                       'Du', 'Sn', 'En', 'Pc', 'Od',
                                       'Ro', 'Rd', 'Ra', 'So', 'Tn', 'Tp', 'Pn', 'Pa', 'Cl', 'Oy', 'Bp']

ROVI_LANG_SCHEMA                 = get_schema(ROVI_LANG_FIELDS)

ROVI_CREW_FIELDS                    = ['Gi', 'Sk', 'Ti', 'Vt', 'Bd', 'Sx', 'Fd', 'Ak', 'Ol', 'Xt', 'Bn', 'Bi', 'De', 'Tl', 'Dd', 'Zc']
ROVI_CREW_SCHEMA                    = get_schema(ROVI_CREW_FIELDS)

TV_VTV_ONLY_SEED_MOVIE              = set(ROVI_PROGRAM_FIELDS).intersection(TV_SEED_MOVIE_SCHEMA_FIELDS)
TV_VTV_ONLY_SEED_TVSERIES           = set(ROVI_PROGRAM_FIELDS).intersection(TV_SEED_TVSERIES_SCHEMA_FIELDS)
TV_VTV_ONLY_SEED_EPISODE            = set(ROVI_PROGRAM_FIELDS).intersection(TV_SEED_EPISODE_SCHEMA_FIELDS)

# SEED SOURCE SCHEMA
# NETFLIX SCHEMA
NETFLIX_GENRES_FIELDS               = ['Tt', 'Ng']
NETFLIX_GENRES_SCHEMA               = get_schema(NETFLIX_GENRES_FIELDS)

NETFLIX_AVAILABILITY_FIELDS         = ['Sk', 'Fm']
NETFLIX_AVAILABILITY_SCHEMA         = get_schema(NETFLIX_AVAILABILITY_FIELDS)

NETFLIX_SOURCE_MERGE_MAP_FIELDS     = ['Au', 'Gi']
NETFLIX_SOURCE_MERGE_MAP_SCHEMA     = get_schema(NETFLIX_SOURCE_MERGE_MAP_FIELDS)

NETFLIX_MOVIES_FIELDS               = ['Sk', 'Ti', 'De', 'Od', 'Ry', 'Ge']
NETFLIX_MOVIES_SCHEMA               = get_schema(NETFLIX_MOVIES_FIELDS)

NETFLIX_TVSHOWS_FIELDS              = ['Sk', 'Ti', 'De', 'Od', 'Ry', 'Ge']
NETFLIX_TVSHOWS_SCHEMA              = get_schema(NETFLIX_TVSHOWS_FIELDS)

NETFLIX_EPISODES_FIELDS             = ['Sk', 'Pk', 'Tk', 'Vt', 'Ti', 'De', 'Sn', 'En', 'Od', 'Ry', 'Ge']
NETFLIX_EPISODES_SCHEMA             = get_schema(NETFLIX_EPISODES_FIELDS)

NETFLIX_SEASONS_FIELDS              = ['Sk', 'Tk', 'Ti', 'De', 'Sn', 'Od', 'Ry', 'Ge']
NETFLIX_SEASONS_SCHEMA              = get_schema(NETFLIX_SEASONS_FIELDS)

NETFLIX_PERSONS_FIELDS              = ['Pt', 'Pk', 'Pi', 'Ti', 'De', 'Rl']
NETFLIX_PERSONS_SCHEMA              = get_schema(NETFLIX_PERSONS_FIELDS)

NETFLIX_RELATED_PROGRAMS_FIELDS     = ['Pk', 'Pt', 'Rk', 'Rr']
NETFLIX_RELATED_PROGRAMS_SCHEMA     = get_schema(NETFLIX_RELATED_PROGRAMS_FIELDS)

#ROTTEN TOMATOES
ROTTEN_TOMATOES_META_FIELDS         = ['Tt', 'Ge', 'Ts']
ROTTEN_TOMATOES_META_SCHEMA         = get_schema(ROTTEN_TOMATOES_META_FIELDS)

#IMDB WIKI CHARACTER_MERGE
IMDB_WIKI_CHARACTER_MERGE_FIELDS    = ['Tt', 'Gi', 'Wt']
IMDB_WIKI_CHARACTER_MERGE_SCHEMA    = get_schema(IMDB_WIKI_CHARACTER_MERGE_FIELDS)

IMDB_CHARACTER_DUPLICATES_FIELDS    = ['Ch']
IMDB_CHARACTER_DUPLICATES_SCHEMA    = get_schema(IMDB_CHARACTER_DUPLICATES_FIELDS)

IMDB_CHARACTERS_FIELDS              = ['Ch', 'Ti', 'Ak', 'Ge', 'Ke', 'De']
IMDB_CHARACTERS_SCHEMA              = get_schema(IMDB_CHARACTERS_FIELDS)

IMDB_CHARACTER_FILMS_FIELDS         = ['Ch', 'Tt', 'Ts', 'Nm']
IMDB_CHARACTER_FILMS_SCHEMA         = get_schema(IMDB_CHARACTER_FILMS_FIELDS)

IMDB_CHARACTER_MAP_FIELDS           = ['Ch', 'Wt']
IMDB_CHARACTER_MAP_SCHEMA           = get_schema(IMDB_CHARACTER_MAP_FIELDS)

#IMDB GENRE BROWSE
IMDB_GENRE_BROWSE_FIELDS            = ['Tt', 'Ge']
IMDB_GENRE_BROWSE_SCHEMA            = get_schema(IMDB_GENRE_BROWSE_FIELDS)

#IMDB IMAGES
IMDB_IMAGES_FIELDS                  = ['Tt', 'Ii', 'Tl']
IMDB_IMAGES_SCHEMA                  = get_schema(IMDB_IMAGES_FIELDS)

#TV_DOT_COM
TV_DOT_COM_META_FIELDS              = ['Gi', 'Im', 'Ge', 'Ed']
TV_DOT_COM_META_SCHEMA              = get_schema(TV_DOT_COM_META_FIELDS)

TV_DOT_COM_GUID_TO_PERSON_FIELDS    = ['Gi', 'Cr']
TV_DOT_COM_GUID_TO_PERSON_SCHEMA    = get_schema(TV_DOT_COM_GUID_TO_PERSON_FIELDS)

#BOXOFFICEMOJO
BOXOFFICEMOJO_META_FIELDS           = ['Gi', 'Ge', 'Ca', 'Di']
BOXOFFICEMOJO_META_SCHEMA           = get_schema(BOXOFFICEMOJO_META_FIELDS)

OTHER_POPULARITY_FIELDS             = ['Gi', 'Rg', 'Bp']
OTHER_POPULARITY_SCHEMA             = get_schema(OTHER_POPULARITY_FIELDS)

#IMAGEDB
BEST_IMAGE_FIELDS                   = ['Gi', 'Im', 'Ar']
BEST_IMAGE_SCHEMA                   = get_schema(BEST_IMAGE_FIELDS)

WIKI_IMAGES_FIELDS                  = ['Gi', 'Im']
WIKI_IMAGES_SCHEMA                  = get_schema(WIKI_IMAGES_FIELDS)

IMAGE_META_FIELDS                   = ['Sk', 'Gi', 'Im']
IMAGE_META_SCHEMA                   = get_schema(IMAGE_META_FIELDS)

#SEED DB
IMDB_COMPANIES_MAP_FIELDS           = ['Cm', 'Ge']
IMDB_COMPANIES_MAP_SCHEMA           = get_schema(IMDB_COMPANIES_MAP_FIELDS)

AMBIGUOUS_UNAMBIGUOS_GENRE_FIELDS   = ['Am', 'Um']
AMBIGUOUS_UNAMBIGUOS_GENRE_SCHEMA   = get_schema(AMBIGUOUS_UNAMBIGUOS_GENRE_FIELDS)

SUBGENRE_GENRE_MAP_FIELDS           = ['Su', 'Sg', 'Gl', 'Ge']
SUBGENRE_GENRE_MAP_SCHEMA           = get_schema(SUBGENRE_GENRE_MAP_FIELDS)

GENRE_HIERARCHY_FIELDS              = ['Pa', 'Pg', 'Ch', 'Cg']
GENRE_HIERARCHY_SCHEMA              = get_schema(GENRE_HIERARCHY_FIELDS)

WIKI_TITLE_CATEGORIES_FIELDS        = ['Gi', 'Ct']
WIKI_TITLE_CATEGORIES_SCHEMA        = get_schema(WIKI_TITLE_CATEGORIES_FIELDS)

GENRE_PHRASES_FIELDS                = ['Ph', 'Gi', 'Wt']
GENRE_PHRASES_SCHEMA                = get_schema(GENRE_PHRASES_FIELDS)

CHANNELS_FIELDS                     = ['Gi', 'Ti', 'Ak', 'Af', 'Cs', 'Ge', 'Ik', 'Is', 'Cp', 'Rp', 'Co', 'Tr', 'Mi', 'Ri', 'Ih', 'Ip', 'Ss', 'Il', 'Tz', 'Im', 'Ct', 'Rt', 'Tg', 'Ll', 'Si', 'Ow', 'Ib', 'Bi', 'Sp', 'Li', 'Lp', 'Rs']
CHANNELS_SCHEMA                     = get_schema(CHANNELS_FIELDS)

AFFILIATIONS_FIELDS                 = ['Gi', 'Ti', 'Af', 'Im', 'Ak', 'Bp', 'Rp', 'Ow', 'Tg', 'Bb', 'Rb']
AFFILIATIONS_SCHEMA                 = get_schema(AFFILIATIONS_FIELDS)

STATIC_GENRES_FIELDS                = ['Gi', 'Ge']
STATIC_GENRES_SCHEMA                = get_schema(STATIC_GENRES_FIELDS)

GENRE_MOVIES_FIELDS                 = ['Gi', 'Ge']
GENRE_MOVIES_SCHEMA                 = get_schema(GENRE_MOVIES_FIELDS)

CONSTANT_POP_FIELDS                 = ['Gi', 'Bp']
CONSTANT_POP_SCHEMA                 = get_schema(CONSTANT_POP_FIELDS)

PRODUCTION_COMPANYS_FIELDS           = ['Gi', 'Vt', 'Ti', 'Ak']
PRODUCTION_COMPANYS_SCHEMA           = get_schema(PRODUCTION_COMPANYS_FIELDS)

#CHANNEL DB
ORIGINAL_AIR_CHANNELS_FIELDS           = ['Gi', 'Vt', 'Ti', 'Ak']
ORIGINAL_AIR_CHANNELS_SCHEMA           = get_schema(ORIGINAL_AIR_CHANNELS_FIELDS)

#SAP
SAP_FOLD_FIELDS =   ['Gi', 'Ti', 'Ty', 'Fi']
SAP_FOLD_SCHEMA = get_schema(SAP_FOLD_FIELDS)
SAP_BIG_FOLD_FIELDS = ['Gi']
SAP_BIG_FOLD_SCHEMA = get_schema(SAP_BIG_FOLD_FIELDS)
SAP_MASHUP_FOLD_FIELDS = ['Gi', 'Ti', 'Ty', 'Fl', 'Rl']
SAP_MASHUP_FOLD_SCHEMA = get_schema(SAP_MASHUP_FOLD_FIELDS)
SAP_INDEX_FIELDS = ['Gi', 'In', 'Pt', 'Ar', 'De', 'Sw']
SAP_INDEX_SCHEMA = get_schema(SAP_INDEX_FIELDS)
SAP_EMP_MC_FIELDS = ['Gi', 'Vt', 'Ti', 'Ig', 'Ge', 'Mi', 'Rd']
SAP_EMP_MC_SCHEMA = get_schema(SAP_EMP_MC_FIELDS)
SAP_FOLD_MC_FIELDS = ['Gi', 'Ti', 'Ak', 'Ik', 'Vt', 'Rd', 'Lt', 'Lg', 'Tg']
SAP_FOLD_MC_SCHEMA = get_schema(SAP_FOLD_MC_FIELDS)
SAP_POP_FIELDS = ['Gi', 'Bp']
SAP_POP_SCHEMA = get_schema(SAP_POP_FIELDS)
SAP_STEM_FIELDS = ['Ti', 'Vt', 'Sy', 'Sv']
SAP_STEM_SCHEMA = get_schema(SAP_STEM_FIELDS)
#APPS DATASPACE SCHEMA
APPS_MC_SCHEMA_FIELDS               = ['Gi', 'Ti', 'De', 'Ke', 'Sk', 'Ca', 'Ge', 'Rd', 'Sr', 'Li', 'Im', 'Kw', 'Bp', 'Vt', 'Ig', 'Ak', 'Ik', 'Ar', 'Fd', 'Lt', 'Lg', 'Ct', 'St', 'Cl', 'Tg', 'Ug', 'Lk']
APPS_FOLD_SCHEMA_FIELDS             = ['Gi', 'Ty', 'Ti', 'Fi', 'Tg']
APPS_POP_SCHEMA_FIELDS              = ['Gi', 'Ti', 'Bp']
APPS_FILTER_SCHEMA_FIELDS           = ['Gi', 'Vf']

#YPAGES DATASPACE SCHEMA
YPAGES_MC_SCHEMA_FIELDS             = ['Gi', 'Ti', 'Vt', 'Ak', 'Ig', 'Pi', 'Em', 'Ad', 'Ct', 'St', 'Cl', 'Zi', 'Pn', 'Lt', 'Lg', 'Wb', 'Ge', 'Rd', 'Tg', 'Fd', 'Sn', 'Lk', 'Ke']
YPAGES_FOLD_SCHEMA_FIELDS           = ['Gi', 'Ty', 'Ti', 'Fi']
YPAGES_POP_SCHEMA_FIELDS            = ['Gi', 'Ti', 'Bp']
YPAGES_GENRE_PREFERENCE_SCHEMA_FIELDS = ['Gi', 'Ti', 'Sc', 'Tg', 'Wt']
YPAGES_CLIPS_BIG_FOLD_SCHEMA_FIELDS = ['Gi', 'Ti']

#freebase datagen
FREEBASE_MOVIE_FIELDS = ['Gi', 'Ti', 'Sk', 'Ig', 'Ak', 'Ke', 'Ad', 'Ap', 'Ge', 'Rd', 'Vt', 'Wr', 'Cl', 'Dn', 'Ca', 'Ho', 'Od', 'Ry', 'En', 'Sn', 'Pi', 'Di', 'Pr', 'Ep', 'Tl', 'Sq', 'Pq', 'Du', 'Ra', 'Ds', 'Pc', 'Ll', 'Co', 'Lo', 'La', 'Ol', 'Oa', 'Me', 'Oe', 'Uc', 'Zc']
FREEBASE_MOVIE_MC_FIELDS = ['Gi', 'Ti', 'Sk', 'Ig', 'Ak', 'Ke', 'Ad', 'Ap', 'Ge', 'Rd', 'Vt', 'Wr', 'Cl', 'Dn', 'Ca', 'Ho', 'Od', 'Ry', 'En', 'Sn', 'Pi', 'Di', 'Pr', 'Ep', 'Tl', 'Sq', 'Pq', 'Du', 'Ra', 'Ds', 'Pc', 'Ll', 'Co', 'Lo', 'La', 'Ol', 'Oa', 'Me', 'Oe', 'Uc', 'Zc']
FREEBASE_MOVIE_SCHEMA = get_schema(FREEBASE_MOVIE_FIELDS)
FREEBASE_MOVIE_MC_SCHEMA = get_schema(FREEBASE_MOVIE_MC_FIELDS)
FREEBASE_PERSONS_FIELDS = ['Gi', 'Ti', 'Sk', 'Bd', 'Dd', 'Rd', 'Oc', 'Br', 'Ak', 'Xt', 'Nt', 'Pa', 'Ch', 'Ma', 'Sb', 'Sx', 'Sp', 'Ol', 'Oa', 'Me', 'Vt', 'Bm', 'Ro' ]
FREEBASE_PERSONS_MC_FIELDS = ['Gi', 'Ti', 'Sk', 'Bd', 'Dd', 'Rd', 'Oc', 'Br', 'Ak', 'Xt', 'Nt', 'Pa', 'Ch', 'Ma', 'Sb', 'Sx', 'Sp', 'Ol', 'Oa', 'Vt', 'Bm', 'Ro' ]
FREEBASE_PERSONS_SCHEMA = get_schema(FREEBASE_PERSONS_FIELDS)
FREEBASE_PERSONS_MC_SCHEMA = get_schema(FREEBASE_PERSONS_MC_FIELDS)
FREEBASE_ROLE_FIELDS = [ 'Gi', 'Sk', 'Ti', 'Ak', 'Pa', 'Sp', 'Rn', 'Ol', 'Oa', 'Oc', 'Rd', 'Vt', 'Up']
FREEBASE_ROLE_SCHEMA = get_schema(FREEBASE_ROLE_FIELDS)
FREEBASE_WEBSITE_FIELDS = ['Gi', 'Sk', 'Ti', 'Ge', 'Pd', 'St', 'Ur' ]
FREEBASE_WEBSITE_SCHEMA = get_schema(FREEBASE_WEBSITE_FIELDS)
FREEBASE_DESCRIPTION_FIELDS = [ 'Gi', 'Sk', 'Ti', 'De', 'Ll' ]
FREEBASE_DESCRIPTION_SCHEMA = get_schema(FREEBASE_DESCRIPTION_FIELDS)
FREEBASE_MISC_FIELDS = [ 'Sk', 'Vt', 'Xt' ]
FREEBASE_MISC_SCHEMA = get_schema(FREEBASE_MISC_FIELDS)
FREEBASE_FOLD_FIELDS = [ 'Gi', 'Sk', 'Ti', 'Ak', 'Rd', 'Vt', 'Xt' ]
FREEBASE_FOLD_SCHEMA = get_schema(FREEBASE_FOLD_FIELDS)
FREEBASE_SEQUEL_FIELDS = [ 'Gi', 'Sk', 'Ti', 'Fi', 'Wg', 'Vt' ]
FREEBASE_SEQUEL_SCHEMA = get_schema(FREEBASE_SEQUEL_FIELDS)
FREEBASE_CONNECTED_SMART_TAGS_FIELDS = [ 'Gi', 'Ti', 'Cg' ]
FREEBASE_CONNECTED_SMART_TAGS_SCHEMA = get_schema(FREEBASE_CONNECTED_SMART_TAGS_FIELDS)
FREEBASE_AWARDS_FIELDS =  ['Sk', 'Ca', 'Da', 'Ce', 'Ti', 'Wo', 'Wi']
FREEBASE_AWARDS_SCHEMA = get_schema(FREEBASE_AWARDS_FIELDS)
FREEBASE_AWARD_CATEGORIES_FIELDS = [ 'Gi', 'Sk', 'Rd', 'Ti' ]
FREEBASE_AWARD_CATEGORIES_SCHEMA = get_schema(FREEBASE_AWARD_CATEGORIES_FIELDS)

#role datagen
ROLE_FIELDS = ['Gi', 'Vt', 'Ti', 'Ak', 'Sk', 'Pa', 'Oc', 'Rd', 'Oa', 'Ol', 'Cg']
ROLE_SCHEMA = get_schema(ROLE_FIELDS)

#phrase server datagen
GID_META_FIELDS = ['Gi', 'Ti', 'Bp', 'Vt', 'Tg', 'Do', 'Xt', 'Np',  'Sx', 'Bd', 'Du', 'Od', 'Ry', 'Mv', 'Cr', 'Cs', 'Af', 'Sp', 'Pp', \
                    'Bm', 'Td', 'Pi', 'Sq', 'Te', 'On', 'Ge', 'Ro', 'To', 'Fd', 'Tl', 'Wl', 'Bl', 'Sm', 'Sl', 'Cd', 'Fi', 'Cp', 'Vl']
GID_META_SCHEMA = get_schema(GID_META_FIELDS)
PHRASE_LIST_FIELDS = ['Ti', 'Ty', 'Ms']
PHRASE_LIST_SCHEMA = get_schema(PHRASE_LIST_FIELDS)
GID_INFO_FIELDS = ['Gi', 'Ti', 'If']
GID_INFO_SCHEMA = get_schema(GID_INFO_FIELDS)
PHRASE_ADDITIONAL_META_FIELDS = ['Gi', 'Vt', 'Xt', 'Bp', 'Cp']
PHRASE_ADDITIONAL_META_SCHEMA = get_schema(PHRASE_ADDITIONAL_META_FIELDS)

#SAP phrase server datagen
SAP_GID_META_FIELDS = ['Gi', 'Ti', 'Bp', 'Vt', 'Tg', 'Gs']
SAP_GID_META_SCHEMA = get_schema(SAP_GID_META_FIELDS)

DEFAULT_CREW_AK_WT = 50
PENALIZED_AK_WT = 50
DEFAULT_AK_WT = 100

# Domains datagen
DOMAIN_FIELDS = ['Gi', 'Ti', 'Do']
DOMAIN_SCHEMA = get_schema(DOMAIN_FIELDS)

# star type datagen
STAR_TYPE_FIELDS = ['Gi', 'Ti', 'Xt']
STAR_TYPE_SCHEMA = get_schema(STAR_TYPE_FIELDS)

# Role merge
CONNECTED_SMARTTAG_FILE_FIELDS = ['Gi', 'Ti', 'Cg']
CONNECTED_SMARTTAG_FILE_SCHEMA = get_schema(CONNECTED_SMARTTAG_FILE_FIELDS)

#Rovi music data
ROVI_ARTIST_FIELDS = ['Gi', 'Ti', 'Vt', 'Ak', 'Bd', 'Br', 'Dd', 'Sx', 'Bm', 'Xt', 'Ip', 'Ge', 'Gg',
                      'Ds', 'Da', 'Ac', 'Ib', 'Nv', 'Dc', 'Im', 'De', 'Pp', 'Rd', 'Tg', 'Cr', 'Ao', 'Cn' ]
ROVI_ARTIST_SCHEMA = get_schema(ROVI_ARTIST_FIELDS)

ROVI_TRACK_FIELDS = ['Gi', 'Ti', 'Vt', 'Pp', 'Wr', 'Co', 'Al', 'Rd',
'Pr', 'Rc', 'Du', 'Tg', 'Cp', 'Dc', 'In', 'Ge', 'Ct', 'Th', 'Tn']
ROVI_TRACK_SCHEMA = get_schema(ROVI_TRACK_FIELDS)

ROVI_ALBUM_FIELDS = ['Gi', 'Ti', 'Vt', 'Ry', 'Ge', 'Gg', 'Pp', 'Wr', 'Co', 'Od', 'Tg', 'Nv', 'Dc', 'Rd',
                     'Cp', 'Im', 'De', 'Xt', 'Ad', 'Md', 'In']
ROVI_ALBUM_SCHEMA = get_schema(ROVI_ALBUM_FIELDS)

ROVI_MUSIC_FOLD_FIELDS = ['Gi', 'Ti', 'Ak', 'Ry', 'Ig', 'Vt', 'Xt', 'Tg']
ROVI_MUSIC_FOLD_SCHEMA = get_schema(ROVI_MUSIC_FOLD_FIELDS)

ROVI_MUSIC_RECOMMENDATION_FIELDS = [ 'Gi', 'Ti', 'Rl', 'Vt', 'Xt' ]
ROVI_MUSIC_RECOMMENDATION_SCHEMA = get_schema(ROVI_MUSIC_RECOMMENDATION_FIELDS)

MUSIC_SERVER_TRACK_FIELDS = ['Gi', 'Ti', 'Vt', 'Al', 'Co', 'Du', 'Ig', 'Pp', 'Tl', 'So', 'Tg', 'Wr', 'Im', 'Dc', 'Fd', 'Cp', 'Ge' ]
MUSIC_SERVER_TRACK_SCHEMA = get_schema(MUSIC_SERVER_TRACK_FIELDS)

CUR_MUSIC_SERVER_TRACK_FIELDS = copy(MUSIC_SERVER_TRACK_FIELDS)
CUR_MUSIC_SERVER_TRACK_FIELDS.extend(['Da', 'Zc'])
CUR_MUSIC_SERVER_TRACK_SCHEMA = get_schema(CUR_MUSIC_SERVER_TRACK_FIELDS)

MUSIC_SERVER_SONG_FIELDS = ['Gi', 'Ti', 'Vt', 'Ak', 'Co', 'Ig', 'Pp', 'Tl', 'Sk', 'Tg', 'Wr', 'Im', 'Cc']
MUSIC_SERVER_SONG_SCHEMA = get_schema(MUSIC_SERVER_SONG_FIELDS)

MUSIC_SERVER_ALBUM_FIELDS = ['Gi', 'Ti', 'Vt', 'Ak', 'Co', 'Ge', 'Ig', 'Od', 'Pp', 'Tl', 'Ry', 'Tg', 'Wr', 'Im', 'Dc', 'Fd',
                             'Gg', 'De', 'Xt' ]
MUSIC_SERVER_ALBUM_SCHEMA = get_schema(MUSIC_SERVER_ALBUM_FIELDS)

CUR_MUSIC_SERVER_ALBUM_FIELDS = copy(MUSIC_SERVER_ALBUM_FIELDS)
CUR_MUSIC_SERVER_ALBUM_FIELDS.append('Cr')
CUR_MUSIC_SERVER_ALBUM_SCHEMA = get_schema(CUR_MUSIC_SERVER_ALBUM_FIELDS)

MUSIC_SERVER_ARTIST_FIELDS = ['Gi', 'Ti', 'Vt', 'Ac', 'Ak', 'Da', 'Tl', 'Tg', 'Im', 'Dc', 'Fd', 'Ge', 'Gg', 'Pp', 'De', 'Bm', 'Ig', 'Db' ]
MUSIC_SERVER_ARTIST_SCHEMA = get_schema(MUSIC_SERVER_ARTIST_FIELDS)

MUSIC_SERVER_GENRE_FIELDS = ['Gi', 'Ti', 'Ak', 'Ry', 'Ig', 'Vt', 'Xt', 'Wt', 'Tg']
MUSIC_SERVER_GENRE_SCHEMA = get_schema(MUSIC_SERVER_GENRE_FIELDS)

MUSIC_SERVER_LEXICAL_FIELDS = ['Gi', 'Ti', 'Vt', 'Bs', 'Sk', 'Tg']
MUSIC_SERVER_LEXICAL_SCHEMA = get_schema(MUSIC_SERVER_LEXICAL_FIELDS)

MUSIC_SERVER_TRENDING_FIELDS = ['Gi', 'Ti', 'Vt']
MUSIC_SERVER_TRENDING_SCHEMA = get_schema(MUSIC_SERVER_TRENDING_FIELDS)

MUSIC_TEMPORAL_FIELDS = ['Gi', 'Ti', 'Vt', 'Sr', 'Tg']
MUSIC_TEMPORAL_SCHEMA = get_schema(MUSIC_TEMPORAL_FIELDS)

CUR_ARTIST_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ge', 'Rd', 'Fd' ]
CUR_ARTIST_SCHEMA = get_schema(CUR_ARTIST_FIELDS)

CUR_ALBUM_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ry', 'Rd', 'Pp', 'Ge', 'Fd' ]
CUR_ALBUM_SCHEMA = get_schema(CUR_ALBUM_FIELDS)

CUR_TRACK_FIELDS = [ 'Gi', 'Ti', 'Rd', 'Tg', 'Du', 'Pp', 'Al', 'Vt', 'Rc', 'Ge', 'Fd', 'Tn', 'Dn', 'Da', 'Zc' ]
CUR_TRACK_SCHEMA = get_schema(CUR_TRACK_FIELDS)

CUR_SEED_ARTIST_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ge', 'Rd', 'Fd', 'Dc', 'Im', 'Gg', 'Xt', 'Ak', 'Sx', 'Bd', 'Br', 'Dd', 'Ac', 'Bm' ]
CUR_SEED_ARTIST_SCHEMA = get_schema(CUR_SEED_ARTIST_FIELDS)

CUR_SEED_ALBUM_FIELDS = [ 'Gi', 'Ti', 'Vt', 'Ry', 'Rd', 'Pp', 'Ge', 'Fd', 'Dc', 'Tg', 'Im', 'Gg', 'Od', 'Wr', 'Co' ]
CUR_SEED_ALBUM_SCHEMA = get_schema(CUR_SEED_ALBUM_FIELDS)

CUR_SEED_TRACK_FIELDS = [ 'Gi', 'Ti', 'Rd', 'Tg', 'Du', 'Pp', 'Al', 'Vt', 'Rc', 'Ge', 'Fd', 'Wr', 'Co' ]
CUR_SEED_TRACK_SCHEMA = get_schema(CUR_SEED_TRACK_FIELDS)

CUR8_FIELDS = [ 'Gi', 'Ti', 'Ak', 'Vt', 'Tl', 'Pp', 'De', 'Da', 'Tg' ]
CUR8_SCHEMA = get_schema(CUR8_FIELDS)

#ACE input schema
ACE_FIELDS = [
    'Gi', 'Ti', 'Vt', 'Ot', 'Sk', 'Ep', 'Ae', 'Pi', 'Ry', 'Od', 'Oy', 'Ak', 'Va', \
    'Ke', 'De', 'Ig', 'Di', 'Pr', 'Ho', 'Wr', 'Co', 'Ic', 'Ge', 'Gg', 'Cl', 'Sm', \
    'Ll', 'Ra', 'Sn', 'En', 'Mi', 'Sq', 'Np', 'Pa', 'To', 'Te', 'Sp', 'Pn', 'Tp', \
    'Wi', 'Ht', 'Se', 'Im', 'Ip', 'Fy', 'Cs', 'Oc', 'Af', 'Ow', 'Cp', 'Og', 'Id', \
    'Fd', 'Lg', 'Lt', 'Bs', 'Is', 'Tl', 'Ps', 'Tg', 'Rd', 'Ng', 'Ur', 'Du', 'Pt', \
    'Sr', 'Zc', 'Zl', 'Aw', 'Ro', 'Xt', 'Rk', 'Rv', 'Po', 'So', 'Sx', 'Cd', 'Gs', \
    'On', 'Fi', 'Fg', 'Pc', 'Ag', 'Ac', 'Xr', 'Lu', 'Ca', 'Me'
]

ACE_SCHEMA = get_schema(ACE_FIELDS)

# TVPublish data
TVPUB_MC_FIELDS = [
    'Gi', 'Ti', 'Vt', 'Ot', 'Sk', 'Ep', 'Ae', 'Pi', 'Ry', 'Od', 'Ak', 'Va', 'Ik', \
    'Ke', 'De', 'Ig', 'Di', 'Pr', 'Ho', 'Wr', 'Co', 'Ic', 'Ge', 'Gg', 'Cl', \
    'Ll', 'Ra', 'Sn', 'En', 'Mi', 'Sq', 'Np', 'Pa', 'To', 'Te', 'Sp', 'Gs', \
    'Wi', 'Ht', 'Sa', 'Im', 'Ip', 'Fy', 'Cs', 'Oc', 'Af', 'Ow', 'Cp', 'Og', 'Id', \
    'Fd', 'Lg', 'Lt', 'Bs', 'Is', 'Tl', 'Ps', 'Tg', 'Rd', 'Ng', 'Ur', 'Du', 'Pt', \
    'Sr', 'Zc', 'Zl', 'Aw', 'Ro', 'Xt', 'Rk', 'Rv', 'Po', 'So', 'Sl', 'Cd', \
    'On', 'Fi', 'Fg', 'Pc', 'Ag', 'Ac', 'Xr', 'Lu', 'Rt', 'Dt'
]

TVPUB_MC_SCHEMA = dict([(x, i) for i, x in enumerate(TVPUB_MC_FIELDS)])

TVPUB_POP_FIELDS = ['Gi', 'Bp', 'Ty']
TVPUB_POP_SCHEMA = dict([(x, i) for i, x in enumerate(TVPUB_POP_FIELDS)])

TVPUB_FOLD_FIELDS = [ 'Gi', 'Ti', 'Ty', 'Tg', 'De', 'Ik', 'Fi', 'Lo']
TVPUB_FOLD_SCHEMA = dict([(x, i) for i, x in enumerate(TVPUB_FOLD_FIELDS)])

TVPUB_AVAIL_FIELDS = [
    'Gi', 'Si', 'Ci', 'Pi', 'Ty', 'Tg', 'Ra', 'Tl', 'At', 'Cl', 'Fs',
    'St', 'Et', 'Du', 'Li', 'Pv', 'Pd', 'Vi', 'Po', 'Pw',
    'Ur', 'Bt', 'Mt', 'Ht', 'Wd', 'Ap', 'Im', 'Pr', 'Tr', 'Br',
    'Vp', 'Sk', 'Fd', 'Vl', 'Ar', 'Xl'
]
TVPUB_AVAIL_SCHEMA = dict([(x, i) for i, x in enumerate(TVPUB_AVAIL_FIELDS)])

# .merge files that gmrf looks at
TVPUB_MERGE_FIELDS = ['Gi', 'Sk', 'Ik', 'Ig', 'Pi', 'Ch', 'Tg']
TVPUB_MERGE_SCHEMA = dict([(x, i) for i, x in enumerate(TVPUB_MERGE_FIELDS)])

WIKI_EPISODE_FILEDS  = ['Gi', 'Ti', 'De', 'Od', 'Pc', 'Di', 'Wr', 'Sn', 'St', 'Pi', 'Ak', 'En', 'Es', 'Nv', 'Ig', 'Mg']
WIKI_EPISODE_SCHEMA = get_schema(WIKI_EPISODE_FILEDS)

USID_CHAN_FIELDS = [ 'Us', 'Ch', 'Vc' ]
USID_CHAN_SCHEMA = get_schema(USID_CHAN_FIELDS)

REAL_LINEUP_FIELDS = [ 'He', 'Op', 'Us', 'Dv' ]
REAL_LINEUP_SCHEMA = get_schema(REAL_LINEUP_FIELDS)

GENRE_DATA_FIELDS = ['Gi', 'Ti', 'Fg', 'Sg', 'Ge', 'Mg']
GENRE_DATA_SCHEMA = get_schema(GENRE_DATA_FIELDS)

WIKI_IG_FIELDS = ['Ti', 'Ig']
WIKI_IG_SCHEMA = get_schema(WIKI_IG_FIELDS)

# Regular expressions
GID_REGEX = re.compile('(?P<prefix>[A-Za-z]+)(?P<id>\d+)')

#XLIST input schema
XLIST_DEDUP_FIELDS = ['Gi', 'Vt', 'Ot', 'So', 'Sk', 'Rd', 'Me']
XLIST_DEDUP_SCHEMA = get_schema(XLIST_DEDUP_FIELDS)
