#!/usr/bin/perl 

use strict;
use GD;
use Date::Parse;
use LWP::Simple;
use Finance::TA;

my $local_path = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-python-bot";
#my $local_path = "/home/ubuntu/bitmex";

my $binsize = "5m";

my @list;
my @data;
my $period = 1;

# EMA
my $low_ema_period = 34*$period;
my $high_ema_period = 55*$period;
my $slow_ema_period = 160*$period;

my $retCode;
my $begIdx;
my $result;
my @series;
my $faltan_datos;

my @timestamp;
my @low_ema;
my @high_ema;
my @slow_ema;

my $total; 		#total de registros analizados 
my $last;		#ultimo EMA que entrega la funcion TA_EMA
my $delta;		#desplazamiento entre el ultimo EMA y el ultimo registro

#variables que uno usa pa entretenerese un rato
my $n;
my $tmp;


#leo la data correspondiente a el arreglo de velas
$total = read_data_file("$local_path/data/bitmex-$binsize.dat");

# Rearreglo tod en vectores para facilitar su manipulacion
my @unx_dates = map {@$_[0]} @data;   #timestamp
my @open      = map {@$_[1]} @data;   #open
my @high      = map {@$_[2]} @data;   #high
my @low       = map {@$_[3]} @data;   #low
my @close     = map {@$_[4]} @data;   #close
my @volume    = map {@$_[5]} @data;   #volume
my @vwp       = map {@$_[6]} @data;   #vwp
my @trades    = map {@$_[7]} @data;   #trades

#   Analisis de las ema en Close por ahora

calcular_ema("low");
calcular_ema("high");
calcular_ema("slow");
open LOG,">$local_path/data/ema-$binsize.dat"; 
for (my $n=0; $n <= $total; $n++)
   {
   print LOG "$unx_dates[$n],$low_ema[$n],$high_ema[$n],$slow_ema[$n]\n";
   }  
close LOG;

exit();

sub calcular_ema
{
my $tipo = shift;
my $period;
if ($tipo eq "low") {$period = $low_ema_period}
if ($tipo eq "high"){$period = $high_ema_period}
if ($tipo eq "slow"){$period = $slow_ema_period}

# aqui ocurre la magia (tengo que averiguar cual es el numero de datos minimo para las condiciones dadas)
($retCode, $begIdx, $result) = TA_EMA(0, $#close, \@close, $period);

# la funcion TA_EMA entrega los resultado con un subindice desplazado en la matriz
# compenso, desplazo e igualo los subindices de cada una de las respuestas
$last = scalar(@$result)-1;
$delta = $total - $last;

if($retCode == $TA_SUCCESS)
   {
   for $n ($begIdx .. $last)
      {
      $tmp = $result->[$n];
      if ($tipo eq "low") {$low_ema[($n+$delta)]= $tmp;}
      if ($tipo eq "high"){$high_ema[($n+$delta)]= $tmp;}
      if ($tipo eq "slow"){$slow_ema[($n+$delta)]= $tmp;}
      }
   }
else
   {
   die "$retCode : error during TA_EMA"; 
   }

# aqui le doy un valor de NULL a los valores de la matriz que no pueden ser satisfechos por la funcion
# debido a las condiciones iniciales de la misma
$tmp = $total - $last + $begIdx - 1;
for $n (0.. $tmp)
   {
   if ($tipo eq "low") {$low_ema[$n] = "";}
   if ($tipo eq "high"){$high_ema[$n]= "";}
   if ($tipo eq "slow"){$slow_ema[$n]= "";}
   }
}

sub read_data_file
{
my $file = shift;
open(DATA, $file)|| die "Cannot open $file file: $!";
@list = <DATA>;
chop(@list);
close(DATA);

#leo la data del archivo y la guardo en un array

for (my $n=0; $n <=$#list; $n++)
   {
   my @tmp = split ",",($list[$n]);
   for (my $o=0; $o <=8; $o++)
      {
      $data[$n][$o] = $tmp[$o];
      }
   }
return $#list;
}


