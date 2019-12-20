var screenCover = document.getElementById("screenCover");
var close = document.getElementById("close");
var nameResto = document.getElementById("nameResto");
var addressResto = document.getElementById("addressResto");
var linkProfile = document.getElementById("linkProfile");
var map = L.map("map");
//Marker Icons from https://github.com/pointhi/leaflet-color-markers
var redMarkerUrl = 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png';
var greenMarkerUrl = 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png';


close.onclick = function() {
    screenCover.style.display = "none";
};

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    zoom: 11,
    maxZoom: 16,
    minZoom: 11,
    id: 'mapbox/streets-v11',
    accessToken: 'pk.eyJ1IjoiZGFuaTQ1MCIsImEiOiJjazQzZ2N6NHIwNzEwM2VvYjV0czNod2k1In0.EoSQjo_EcbtuCpeRKBEHqw'
}).addTo(map);

//https://stackoverflow.com/questions/30190268/leaflet-how-to-add-click-event-listener-to-popup
function putOnMap(name, address, latAndLong, markerUrl) {
    let myPopUp = L.DomUtil.create('div');
    
    if(address !== undefined){
        myPopUp.innerHTML = '<p class="redirect">' + name + '</p>'; //descr = name;//'<a href="' + '{% url 'blog-map' %}' + '/' + name + '/' + address +'">' + descr + '</a>';
        myPopUp.onclick = function() {
            screenCover.style.display = "block";
            nameResto.innerHTML = name;
            addressResto.innerHTML = address;
            linkProfile.setAttribute("href", "place/" + name.replace(/ /g, "%20"));

        }
    } else {
        myPopUp.innerHTML = name;
    }
    let iconMarker = new L.Icon({
        iconUrl: markerUrl,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    let marker = L.marker(latAndLong, {icon: iconMarker}).addTo(map);
    marker.bindPopup(myPopUp);
    marker.on('mouseover', (e) => {marker.openPopup()});
    return marker;
}

map.locate({setView: true});

map.on('locationfound', (e) => {
    marker = putOnMap("Your current position (approximation)", undefined, e.latlng, greenMarkerUrl);
    map.flyTo(e.latlng, map.maxZoom);
    marker.openPopup();
});
map.on('locationerror', (e) => {
    let notification = document.getElementById("notification");
    notification.style.display = "block";
    map.flyTo([50.85045, 4.34878], map.minZoom);
});