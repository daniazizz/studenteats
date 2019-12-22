function addHoverEffectOn(elements, className1, className2) {
    for(let i = 0; i < elements.length; ++i){
        let element = elements[i];
        element.onmouseover = function() {
            if(!element.classList.contains(className1)){
                for(k = 0; k <= i; ++k){
                    elements[k].classList.add(className1);
                    elements[k].classList.remove(className2);
                }
                for(k = elements.length-1; k > i; --k){
                    if(elements[k].classList.contains(className2)){
                        elements[k].classList.remove(className2);
                    }
                }
            }
        }
    }
}

function addOutFocusEffectOn(elements, className){
    for(let i = 0; i < elements.length; ++i){
        let element = elements[i];
        element.onmouseout = function() {
            if(element.classList.contains(className)){
                for(k = 0; k <= i; ++k){
                    elements[k].classList.remove(className);
                }
            }
        }
    }
}

function addClickEffectOn(elements, className){
    for(let i = 0; i < elements.length; ++i){
        let element = elements[i];
        element.onclick = function() {
            let value = i + 1;
            if(className == "clicked")
                ratingInput.value = value;
            else
                costInput.value = value;
            for(k = 0; k <= i; ++k){
                elements[k].classList.add(className);
            }
        }
    }
}

addHoverEffectOn(stars, "checked", "clicked");
addOutFocusEffectOn(stars, "checked");
addClickEffectOn(stars, "clicked");
addHoverEffectOn(euros, "checked2", "clicked2");
addOutFocusEffectOn(euros, "checked2");
addClickEffectOn(euros, "clicked2");