def date_to_float(stri):
  stri=stri.strip()
  stri=stri.split(':')
  final=float(stri[0])*60
  final=float(stri[1])+final
  final=float(stri[2])/60+final
  return final
