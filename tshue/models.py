from django.db import models

ID_LEN = 15
TYP_LEN = 300
ATTR_LEN = 100
NS_LEN = 20
TYP_LMJ_LEN = 400
TL_LEN = 2000
PRI_LEN = 40
# Create your models here.
class WikiData(models.Model):
    qid = models.CharField(max_length=ID_LEN)			# ID of WikiData
    en_ori = models.CharField(max_length=TYP_LEN)		# English Wikipedia
    zh_ori = models.CharField(max_length=TYP_LEN)		# Chinese Wikipedia
    ja_ori = models.CharField(max_length=TYP_LEN)		# Japanese Wikipedia
    ko_ori = models.CharField(max_length=TYP_LEN)		# Korean Wikipedia
    en = models.CharField(max_length=TYP_LEN)			# English Wikipedia (Stripped note and namespace)
    en_attr = models.CharField(max_length=ATTR_LEN)		# English Wikipedia (括號內的註解)
    en_ns = models.CharField(max_length=NS_LEN)			# English Wikipedia (namespace)
    zh = models.CharField(max_length=TYP_LEN)			# Chinese Wikipedia (Stripped note and namespace)
    zh_attr = models.CharField(max_length=ATTR_LEN)		# Chinese Wikipedia (括號內的註解)
    zh_ns = models.CharField(max_length=NS_LEN)			# Chinese Wikipedia (namespace)
    ja = models.CharField(max_length=TYP_LEN)			# Japanese Wikipedia (Stripped note and namespace)
    ja_attr = models.CharField(max_length=ATTR_LEN)		# Japanese Wikipedia (括號內的註解)
    ja_ns = models.CharField(max_length=NS_LEN)			# Japanese Wikipedia (namespace)
    ko = models.CharField(max_length=TYP_LEN)			# Korean Wikipedia (Stripped note and namespace)
    ko_attr = models.CharField(max_length=ATTR_LEN)		# Korean Wikipedia (括號內的註解)
    ko_ns = models.CharField(max_length=NS_LEN)			# Korean Wikipedia (namespace)

    # 0: 無譯
    # 1: 英譯(音譯1): 舊譯名優先
    # 2: 英譯(音譯2): 全新音譯
    # 3: 中日韓通用
    # 4: 中日通用
    # 5: 中韓通用
    # 6: 日韓通用
    # 7: 中譯(漢字直譯)
    # 8: 日譯(漢字直譯)
    # 9: 韓譯(漢字直譯) (reserved)
    # 10: 中譯
    typ0 = models.CharField(max_length=TYP_LEN)					# 無譯
    typ_lmj0 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 無譯
    typ1 = models.CharField(max_length=TYP_LEN)					# 英譯(音譯1): 舊譯名優先
    typ_lmj1 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 英譯(音譯1)
    typ_tl1 = models.CharField(max_length=TL_LEN)				# Tokenlist of 英譯(音譯1)
    typ2 = models.CharField(max_length=TYP_LEN)					# 英譯(音譯2): 全新音譯
    typ_lmj2 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 英譯(音譯2)
    typ_tl2 = models.CharField(max_length=TL_LEN)				# Tokenlist of 英譯(音譯2)
    typ3 = models.CharField(max_length=TYP_LEN)					# 中日韓通用
    typ_lmj3 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 中日韓通用
    typ4 = models.CharField(max_length=TYP_LEN)					# 中日通用
    typ_lmj4 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 中日通用
    typ5 = models.CharField(max_length=TYP_LEN)					# 中韓通用
    typ_lmj5 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 中韓通用
    typ6 = models.CharField(max_length=TYP_LEN)					# 日韓通用
    typ_lmj6 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 日韓通用
    typ7 = models.CharField(max_length=TYP_LEN)					# 中譯(漢字直譯)
    typ_lmj7 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 中譯(漢字直譯)
    typ8 = models.CharField(max_length=TYP_LEN)					# 日譯(漢字直譯)
    typ_lmj8 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 日譯(漢字直譯)
    typ9 = models.CharField(max_length=TYP_LEN)					# 韓譯(漢字直譯)
    typ_lmj9 = models.CharField(max_length=TYP_LMJ_LEN)			# Lomaji of 韓譯(漢字直譯)
    typ10 = models.CharField(max_length=TYP_LEN)				# 中譯
    typ_lmj10 = models.CharField(max_length=TYP_LMJ_LEN)		# Lomaji of 中譯
    chosen_typ = models.CharField(max_length=TYP_LEN)			# 最佳翻譯
    chosen_typ_lmj = models.CharField(max_length=TYP_LMJ_LEN)	# Lomaji of 最佳翻譯
    chosen_typ_tl = models.CharField(max_length=TL_LEN)			# TokenList of 最佳翻譯
    pri = models.CharField(max_length=PRI_LEN)					# 翻譯優先序

    manual_modified = models.BooleanField()						# 是否已人工訂正

