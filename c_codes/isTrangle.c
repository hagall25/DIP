int isTriangle(int a, int b, int c, int d){
    if(a<0 || b<0 || c<0){
        return -1;
    }
    if ((a >= (b + c)) && ((a + b) <= c) && ((a+c) <= b)){
        return -1;
    } 
    return 1;
}