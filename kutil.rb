#!/usr/bin/env ruby

# reads output from
# pdf2text -layout <pdf> <txt>

DEBUG=0
require 'date'

def process_invoice_text(invoice_text_file)

  status = :header 
  statement_date = nil
  water_consumption_var = 0
  water_rate_var = 0.0
  water_charge_var = 0.0
  sewer_consumption_var = 0
  sewer_rate_var = 0.0
  sewer_charge_var = 0.0
  gas_charges_var = 0.0
  gas_consumption_var = 0.0
  stormwater_charges_var = 0.0
  water_heater_var = 0.0


  File.open(invoice_text_file) do |invoice|
    invoice.each_line do |line|
      line.chomp!
      STDERR.puts "##{status}: #{line}" if DEBUG==1
      if (/Statement Date: (?<datum>[A-Za-z]+ [[:digit:]]+ [[:digit:]]+)/ =~ line)
        statement_date = Date.parse(datum)
        STDERR.puts datum if DEBUG==1
        STDERR.puts statement_date if DEBUG==1
      end
      status = :gas if line.match(/\w*GAS/)
      status = :water if line.match(/\w*WATER/)
      if (status == :water)
        if (/Water[[:space:]]+(?<water>[[:digit:]]+)[[:space:]]+m3[[:space:]]+(?<water_rate>[\.0-9]+)[[:space:]]+(?<water_charge>[\.0-9]+)/ =~ line)
          STDERR.print water, water_rate, water_charge if DEBUG==1
          STDERR.puts line if DEBUG==1
          water_consumption_var += water.to_f
          water_rate_var += water_rate.to_f
          water_charge_var += water_charge.to_f
        end
        if (/Sewer[[:space:]]+(?<sewer>[[:digit:]]+)[[:space:]]+m3[[:space:]]+(?<sewer_rate>[\.0-9]+)[[:space:]]+(?<sewer_charge>[\.0-9]+)/ =~ line)
          STDERR.print sewer, sewer_rate, sewer_charge if DEBUG==1
          STDERR.puts line if DEBUG==1
          sewer_consumption_var += sewer.to_f
          sewer_rate_var += sewer_rate.to_f
          sewer_charge_var += sewer_charge.to_f
        end
      end
      if (status == :gas)
        if (/Gas charges from.*?(?<gas_charges>[\.0-9]+)$/ =~ line)
          gas_charges_var += gas_charges.to_f
        end
        if (/Total Consumption.*?(?<gas_consumption>[0-9]+)/ =~ line)
          STDERR.puts line if DEBUG==1
          STDERR.puts "gas_consumption = #{gas_consumption}" if DEBUG==1
          gas_consumption_var += gas_consumption.to_f
        end
      end

      if (/Total Stormwater Rate Charges.*?(?<stormwater_charges>[\.0-9]+)/ =~ line)
        stormwater_charges_var += stormwater_charges.to_f
        STDERR.puts stormwater_charges_var if DEBUG==1
        STDERR.puts line if DEBUG==1
      end
      if (/Water Heater Rental Charges:\s+(?<water_heater>[\.0-9]+)$/ =~ line)
        water_heater_var = water_heater.to_f
        STDERR.puts line if DEBUG==1
      end
    end
    summary = water_charge_var+sewer_charge_var+gas_charges_var+stormwater_charges_var+water_heater_var
    printf "%s;%.2f;%d;%.2f;%d;%.2f;%.2f;%d;%.2f;%.2f\n", statement_date, summary,
                      water_consumption_var, water_charge_var, sewer_consumption_var, sewer_charge_var, stormwater_charges_var,
                      gas_consumption_var, gas_charges_var,
                      water_heater_var
=begin
    printf "date: %s, summary: $%.2f\n", statement_date, water_charge_var+sewer_charge_var+gas_charges_var+stormwater_charges_var+water_heater_var
    puts "watercomsumption #{water_consumption_var} cbm"
    # puts "water_rate $#{water_rate_var}"
    puts "water $#{water_charge_var}"
    puts "sewer_consumption #{sewer_consumption_var} cbm"
    # puts "sewer rate $#{sewer_rate_var}"
    puts "sewer $#{sewer_charge_var}"
    puts "stormwater $#{stormwater_charges_var}"
    puts "water overall $#{water_charge_var + sewer_charge_var}"
    puts "gas consumption #{gas_consumption_var} cbm"
    puts "gas $#{gas_charges_var}"
    puts "water heater $#{water_heater_var}"
=end
  end
end

def print_header
  puts "date;sum;water;water charge;sewer;sewer charge;stormwater;gas;gas charge;water heater"
end

if $0 == __FILE__
  text_files = ARGV.empty? ? Dir['**/*.txt'] : ARGV
  STDERR.puts "files: #{text_files}" if $VERBOSE

  print_header
  text_files.sort.each do |invoice|
    process_invoice_text(invoice)
  end
end

