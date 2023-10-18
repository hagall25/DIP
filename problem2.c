int foo(int a, int b){
    while(a<3){
        a++;
        while(b<3){
            b++;
        }
    }
    if(a+b>5){
        return 1;
    } else {
        return 0;
    }
}