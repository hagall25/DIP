int foo (int a){
    if(a<3){
        if((a<2 && a >0) || a == -1){
            return 1;
        } else {
            return 2;
        }
    } else {
        if(a < 4){
            return 3;
        } else {
            return 4;
        }
    }
}