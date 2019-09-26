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

#BB
my $optInTimePeriod = 20;
my $optInNbDevUp =2.5;
my $optInNbDevDn = 2.5;
my $optInMAType = 8;

my $outRealUpperBand;
my $outRealMiddleBand;
my $outRealLowerBand;

my $retCode;
my $begIdx;

my @upper_band;
my @middle_band;
my @lower_band;


my $total; 		#total de registros analizados 
my $last;		#ultimo BB que entrega la funcion TA_BBANDS
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


# Calcular  Bollinger Bands
calcular_bb();
open LOG,">$local_path/data/bb-$binsize.dat"; 
for (my $n=0; $n <= $total; $n++)
{
print LOG "$unx_dates[$n],$upper_band[$n],$middle_band[$n],$lower_band[$n]\n";
}
close LOG;

exit();

sub calcular_bb
{
# $optInTimePeriod [Number of period] - integer (optional)
#     default: 5
#     valid range: min=2 max=100000
#
# $optInNbDevUp [Deviation multiplier for upper band] - real number (optional)
#     default: 2
#     valid range: min=-3e+037 max=3e+037
#
# $optInNbDevDn [Deviation multiplier for lower band] - real number (optional)
#     default: 2
#     valid range: min=-3e+037 max=3e+037
#
# $optInMAType [Type of Moving Average] - integer (optional)
#     default: 0
#     valid values: 0=SMA 1=EMA 2=WMA 3=DEMA 4=TEMA 5=TRIMA 6=KAMA 7=MAMA 8=T3
#
# returns: $outRealUpperBand - reference to real values array
# returns: $outRealMiddleBand - reference to real values array
# returns: $outRealLowerBand - reference to real values array

($retCode, $begIdx, $outRealUpperBand, $outRealMiddleBand, $outRealLowerBand) = TA_BBANDS(0, $#close, \@close, $optInTimePeriod, $optInNbDevUp, $optInNbDevDn, $optInMAType);
$last = scalar(@$outRealUpperBand)-1;
$delta = $total - $last;

if($retCode == $TA_SUCCESS)
   {
   for $n ($begIdx .. $last)
      {
      $tmp = $outRealUpperBand->[$n];
      $upper_band[($n+$delta)]= $tmp;

      $tmp = $outRealMiddleBand->[$n];
      $middle_band[($n+$delta)]= $tmp;

      $tmp = $outRealLowerBand->[$n];
      $lower_band[($n+$delta)]= $tmp;
      }
   }
else
   {
   die "$retCode : error during TA_BBANDS"; 
   }
$tmp = $total - $last + $begIdx - 1;
for $n (0.. $tmp)
   {
   $upper_band[$n] = "";
   $middle_band[$n] = "";
   $lower_band[$n] = "";
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


