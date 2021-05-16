
rm(list=ls())
graphics.off()
library(EpiEstim)

## parametri dell'intervallo seriale stimati da dati di contact tracing lombardi
shape.stimato <- 1.87
rate.stimato <- 0.28

## massimo numero di giorni dell'intervallo seriale
N <- 300

## definisco la distribuzione dell'intervallo seriale
intervallo.seriale <- dgamma(0:N, shape=shape.stimato, rate=rate.stimato) 

## normalizzo la distribuzione dell'intervallo seriale in modo che la somma faccia 1
SI <- (intervallo.seriale/sum(intervallo.seriale)) 

#startPoint = 297
for (file_ in c(
    "dpc_nuovi_positivi.Rdata",
    "dpc_ingressi_terapia_intensiva.Rdata",
    "dpc_deceduti.Rdata",
    "dpc_ricoverati_con_sintomi.Rdata",
    "decessi.Rdata",
    "casi_prelievo_diagnosi.Rdata",
    "casi_inizio_sintomi.Rdata",
    "casi_inizio_sintomi_sint.Rdata",
    "curva_epidemica_Italia_ufficiale.Rdata"
    )){

    print(file_)

    ## leggo la curva epidemica da un file con 3 colonne separate da spazi: data, numero di casi trasmessi localmente, numero di casi importati
    curva.epidemica <- read.table(file_)
    curva.epidemica[,1] <- as.Date(curva.epidemica[,1])
    names(curva.epidemica) <- c("dates", "local", "imported") ## assegno i nomi richiesti dal pacchetto EpiEstim

    ## calcolo la stima di R applicando la funzione estimate_R del pacchetto EpiEstim
    stima <- estimate_R(incid=curva.epidemica, method="non_parametric_si", config = make_config(list(si_distr = SI, n1=10000, mcmc_control=make_mcmc_control(thin=1, burnin=1000000))))

    ## il pacchetto avvisa che la stima di Rt viene fornita con una media mobile settimanale ("Default config will estimate R on weekly sliding windows"), eventualmente personalizzabile
    ## avvisa inoltre che la parte iniziale della curva non e' sufficiente alla stima corretta della variabilita' di Rt ("You're estimating R too early in the epidemic to get the desired posterior CV")

    ###################
    ### Attenzione! ###
    ###################

    ## La stima e' calcolata su tutta la curva epidemica specificata, ma il pacchetto non puo' tenere conto dei ritardi di inserimento nel dato
    ## Le stime di Rt varieranno man mano che vengono inseriti nuovi casi con data di inizio sintomi indietro nel tempo
    ## Per questo motivo ISS considera valide le stime fino a 14 giorni prima della data in cui viene effettuata la stima.
    ## Questo ritardo puo' cambiare nel tempo

    ## estraggo i risultati di interesse
    R.medio <- stima$R$`Mean(R)` ## valore medio
    R.lowerCI <- stima$R$`Quantile.0.025(R)` ## estremo inferiore dell'intervallo di confidenza
    R.upperCI <- stima$R$`Quantile.0.975(R)` ## estremo superiore dell'intervallo di confidenza

    ## estraggo le date di riferimento per la stima di R
    ## la data rappresenta il giorno centrale intorno a cui e' calcolata la media mobile di Rt (con finestra di ampiezza pari a una settimana)
    sel.date <- stima$R[, "t_end"]
    date <- curva.epidemica[sel.date,1] 

    startPoint = length(date) - 7*4*7 - 2 ## 1 feb - 1 sep
    ymax = 1.55
    ymin = 0.45
    ysize = 0.1
    ## visualizzazione grafica dei risultati
    par(mar=c(7,5,1,1))
    pdf(file=paste("RPlots",file_,".pdf", sep=""))
    png(file=paste("RPlots",file_,".png", sep=""), width = 1280, height = 768, units='px')
    plot(R.upperCI, type='l', lwd=2, col='gray', axes=FALSE, ylim=c(ymin, ymax), ylab=expression(R[t]), xlab="", xlim=c(startPoint, length(date)))
    lines(R.medio, type='l', lwd=3, col='gray20')
    lines(R.lowerCI, type='l', lwd=2, col='gray')
    axis(1, at=1:length(R.medio), label=date, las=2)
    axis(2, las=2)
    grid((length(date)-startPoint)/7, 12, lwd = 2) # Nx, Ny, size
    print(file_)
}
