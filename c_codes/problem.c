int foo(int a){
    int i = 0;
    while(a<3){
        i = a*2+8/a + 2;
        a++;
    }
    if(i>2){
        return 1;
    } else {
        return 0;
    }
}