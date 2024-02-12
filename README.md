# A5_GraphNeuralNet_PartDynamics
Projekt z przedmiotu Informatyka Systemów Złożonych na kierunku Informatyka Akademii Górniczo-Hutniczej w Krakowie, dotyczący implementacji wybranego modelu boid dynamics.


## Autorzy
- Hubert Czader ([@HubertCzader](https://github.com/HubertCzader))
- Paweł Hanusik ([@pawelhanusik](https://github.com/pawelhanusik))


## Spis treści:
1. [Wybrany model](#1-wybrany-model)
2. [Opis modelu](#2-opis-modelu)
3. [Zebrane dane](#3-zebrane-dane)
4. [Aproksymacja dynamiki agentów przy pomocy GNN'ów](#4-aproksymacja-dynamiki-agentów-przy-pomocy-gnnów)



## 1. Wybrany model

Wizualizacja:

<img src="https://github.com/pawelhanusik/A5_GraphNeuralNet_PartDynamics/blob/master/media/boids.gif" width="70%" height="auto">

---

## 2. Opis modelu:

1. Dane boidów:
    1. Każdy boid jest bytem o wymiarach 15x15.
    1. Każdy porusza się z tą samą prędkością.
    1. Każdy ma określoną pozycję (`pos`) oraz kąt (`a`).
1. Ruch:
    1. Każdy boid porusza się z zadaną prędkością w kierunku zadanego kąta (`a`).
    1. Na podstawie poniższych reguł zmieniany jest kąt (`a`).
1. Reguły (dla każdego boida):
    1. Obliczana jest średnia pozycja (`avg_pos`) oraz średni kąt (`avg_a`) pobliskich boidów, czyli następujących:
        - znajdujące się w oddaleniu o 180
        - z nich wybieranych jest 7 najbliższych.
    1. Jeśli:
        1. Boid jest zbyt blisko innego boida (odległość < 8), to zmienia kąt na taki, który pozwoli mu najszybciej się oddalić.
        1. abs(`avg_pos` - `pos`) < 90, to zmienia kąt na `avg_a`.
        1. abs(`avg_pos` - `pos`) >= 90, to zmienia kąt na taki, który pozwoli mu najszybciej się zbliżyć do avg_pos.
    1. Zmiana aktualnego kąta na ustalony powyżej następuje z prędkością `2.4` stopnia na klatkę.
  
---

## 3. Zebrane dane

Dane zostały zapisane w formacie binarnym. Pierwszy int to liczba boidów. Następnie dla każdej klatki zapisywane są 3 floaty dla każdego boida: x, y, a.

Następnie dane zostały przekonwertowane przy pomocy skryptu `parseDataToNp.py` na dane szeregów czasowych w formacie, który oczekuje na wejściu SwarmNet.

---

## 4. Aproksymacja dynamiki agentów przy pomocy GNN'ów

Do aproksymacji został wykorzystany model `SwarmNet`. Model był uczony przez 100 epok
na danych zebranych z 16 minut symulacji, w której brało udział 50 boidów.

"Długość" danych wejściowych oraz liczba boidów były ograniczone ilością pamięci
RAM (32GB) oraz VRAM (12GB). Proces uczenia trwał ok. 5.5h.

Poniżej przedstawiono wykres lossu podczas uczenia:

![loss](media/zad2-gnn-swarmnet-loss.png)

Wyniki aproksymacji zostały przedstawione na poniższym filmie.  
Boidy niebieskie to boidy z symulacji, boidy czerwone to boidy wygenerowane przez model.


<img src="https://github.com/pawelhanusik/A5_GraphNeuralNet_PartDynamics/blob/master/media/zad2-results.gif" width="70%" height="auto">


Jak widać czerwone boidy w ogóle nie pokrywają się z niebieskimi. Jednak można zauważyć, iż wykazują
się w pewnym stopniu podobnymi zachowaniami.

Można zauważyć odbijanie się od brzegów:

<img src="https://github.com/pawelhanusik/A5_GraphNeuralNet_PartDynamics/blob/master/media/zad2-results-case-border.gif" width="70%" height="auto">

Jak widać brzeg jest przesunięty lekko w dół, jednak dla wszystkich jest w tym samym miejscu.  
Dla lewego brzegu działa analogicznie, jednak dolny i prawy znajdują się "poza mapą", tnz boidy na chwilę znikają, jednak potem wracają.

Poniżej widać grupowanie się boidów, jednak nie wszyscy sąsiedzi są brani pod uwagę.

<img src="https://github.com/pawelhanusik/A5_GraphNeuralNet_PartDynamics/blob/master/media/zad2-results-case-groupping.gif" width="70%" height="auto">

Jak widać stworzyły się dwie grupy: jedna podróżuje w górę, druga w dół. Mimo, iż boidy z tych dwóch grup powinny się odpychać, to jednak nie robią tego.

Dodatkowo na podglądzie ogółu widzimy, że z czasem boidy poprawnie się grupują.
