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

#STOCH
my $outSlowK;
my $outSlowD;
my @slowK;
my @slowD;

# estos tengo que igualarlos a la grafica de bitmex
my $optInFastK_Period = 14*$period; 
my $optInSlowK_Period = 1*$period;
my $optInSlowD_Period = 3*$period;  

my $optInSlowK_MAType = 1;
my $optInSlowD_MAType = 1;

my $retCode;
my $begIdx;


my $total; 		#total de registros analizados 
my $last;		#ultimo STOCH que entrega la funcion TA_STOCH
my $delta;		#desplazamiento entre el ultimo STOCH y el ultimo registro


#variables que uno usa pa entretenerese un rato
my $n;
my $tmp;
my $mediaK;
my $mediaD;

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

calcular_stoch();
#print "$total: $close[$total]\n";
open LOG,">$local_path/data/stoch-$binsize.dat";
for (my $n=0; $n <= $total; $n++)
   {
   if ($n < 4)
      {
      print LOG "$unx_dates[$n],0,0,0\n"; 
      }
   else
      {
      $mediaD = ($slowD[$n]+$slowD[$n-1]+$slowD[$n-2]+$slowD[$n-3]+$slowD[$n-4])/5;
      $mediaK = ($slowK[$n]+$slowK[$n-1]+$slowK[$n-2]+$slowK[$n-3]+$slowK[$n-4])/5;
      print LOG "$unx_dates[$n],$mediaK,$mediaD,0\n";
      } 
   }
exit();

sub calcular_stoch
{
($retCode, $begIdx, $outSlowK, $outSlowD) = TA_STOCH(0, $#close, \@high, \@low, \@close, $optInFastK_Period, $optInSlowK_Period, $optInSlowK_MAType, $optInSlowD_Period, $optInSlowD_MAType);

$last = scalar(@$outSlowK)-1;
$delta = $total - $last;
if($retCode == $TA_SUCCESS)
   {
   for $n ($begIdx .. $last)
      {
      $tmp = $outSlowK->[$n];
      $slowK[($n+$delta)]= $tmp;

      $tmp = $outSlowD->[$n];
      $slowD[($n+$delta)]= $tmp;
      }
   }
else
   {
   die "$retCode : error during TA_STOCH"; 
   }

# aqui le doy un valor de NULL a los valores de la matriz que no pueden ser satisfechos por la funcion
# debido a las condiciones iniciales de la misma

$tmp = $total - $last + $begIdx - 1;
for $n (0.. $tmp)
   {
   $slowK[$n]= "";
   $slowD[$n]= "";
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

