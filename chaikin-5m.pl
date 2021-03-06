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

#chaikin
my @adosc;
my $optInFastPeriod = 4;
my $optInSlowPeriod = 10;

my $result;

my $retCode;
my $begIdx;

my $total; 		#total de registros analizados 
my $last;		#ultimo BB que entrega la funcion TA_ADOSC
my $delta;		#desplazamiento entre el ultimo BB y el ultimo registro


#variables que uno usa pa entretenerese un rato
my $n;
my $tmp;

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


# Calcular  Chaikin
calcular_chaikin();

open LOG,">$local_path/data/chaikin-$binsize.dat"; 
my $max_chaikin;
my $min_chaikin;
my $chaikin;

for (my $n=0; $n <= 14; $n++)
   {
   $chaikin = 0;
   print LOG "$unx_dates[$n],$chaikin,0,0\n";
   }


for (my $n=14; $n <= $total; $n++)
   {
#-178570908.136942×100÷200000000.49889
# %K = (CLOSE - MIN (LOW (%K))) / (MAX (HIGH (%K)) - MIN (LOW (%K))) * 100
# CLOSE – precio de cierre de hoy;
# MIN (LOW (%K)) – el menor de los mínimos para el número de períodos %K;
# MAX (HIGH (%K)) – el mayor de los máximos para el número de períodos %K.
   my $max_chaikin = $adosc[$n-14];
   my $min_chaikin = $adosc[$n-14];
   for (my $p=($n-14); $p<=$n; $p++)
      {
      if (($adosc[$p]) < $min_chaikin) {$min_chaikin = $adosc[$p]}
      if (($adosc[$p]) > $max_chaikin) {$max_chaikin = $adosc[$p]}
      }
   if (($max_chaikin eq 0 ) && ($min_chaikin eq 0) )
      {
      $chaikin = 0;
      }
   else
      {
      $chaikin = (($adosc[$n]-$min_chaikin) / ($max_chaikin-$min_chaikin))*100;
      }
   print LOG "$unx_dates[$n],$chaikin,0,0\n";
   }
close LOG;
exit();

sub calcular_chaikin
{
#(Chaikin A/D Oscillator)
# @high, @low, @close, @volume - real values arrays, all have to be the same size
# $optInFastPeriod [Number of period for the fast MA] - integer (optional)
#     default: 3
#     valid range: min=2 max=100000
# $optInSlowPeriod [Number of period for the slow MA] - integer (optional)
#     default: 10
#     valid range: min=2 max=100000
# returns: $outReal - reference to real values array

# aqui ocurre la magia (tengo que averiguar cual es el numero de datos minimo para las condiciones dadas)
($retCode, $begIdx, $result) = TA_ADOSC(0, $#close, \@high, \@low, \@close, \@volume, $optInFastPeriod, $optInSlowPeriod);

# compenso, desplazo e igualo los subindices de cada una de las respuestas
$last = scalar(@$result)-1;
$delta = $total - $last;
if($retCode == $TA_SUCCESS)
   {
   for $n ($begIdx .. $last)
      {
      $tmp = $result->[$n];
      $adosc[($n+$delta)]= $tmp;
      }
   }
else
   {
   die "$retCode : error during TA_ADOSC"; 
   }

# aqui le doy un valor de NULL a los valores de la matriz que no pueden ser satisfechos por la funcion
# debido a las condiciones iniciales de la misma
$tmp = $total - $last + $begIdx - 1;
for $n (0.. $tmp)
   {
   $adosc[$n] = 0;
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


