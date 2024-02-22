
;; Function foo (foo, funcdef_no=0, decl_uid=1943, cgraph_uid=1, symbol_order=0)

int foo (int a)
{
  int D.1950;

  goto <D.1946>;
  <D.1947>:
  a = a + 1;
  <D.1946>:
  if (a <= 2) goto <D.1949>; else goto <D.1945>;
  <D.1949>:
  if (a > 0) goto <D.1947>; else goto <D.1945>;
  <D.1945>:
  D.1950 = a;
  goto <D.1951>;
  <D.1951>:
  return D.1950;
}


