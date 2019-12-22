function lightUp(rating, lst, className){
    for(i = 0; i < rating; ++i){
        lst[i].classList.add(className);
    }
}