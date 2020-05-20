#!/usr/bin/env ruby

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
  stormwater_charges_var = 0.0
  water_heater_var = 0.0


  File.open(invoice_text_file) do |invoice|
    invoice.each_line do |line|
      line.chomp!
      # puts "##{status}: #{line}"
      if (/Statement Date: (?<datum>[A-Za-z]+ [[:digit:]]+ [[:digit:]]+)/ =~ line)
        statement_date = Date.parse(datum)
        puts datum
        puts statement_date
      end
      status = :gas if line.match(/\w*GAS/)
      status = :water if line.match(/\w*WATER/)
      if (status == :water)
        if (/Water[[:space:]]+(?<water>[[:digit:]]+)[[:space:]]+m3[[:space:]]+(?<water_rate>[\.0-9]+)[[:space:]]+(?<water_charge>[\.0-9]+)/ =~ line)
          # print water, water_rate, water_charge
          # puts line
          water_consumption_var += water.to_f
          water_rate_var += water_rate.to_f
          water_charge_var += water_charge.to_f
        end
        if (/Sewer[[:space:]]+(?<sewer>[[:digit:]]+)[[:space:]]+m3[[:space:]]+(?<sewer_rate>[\.0-9]+)[[:space:]]+(?<sewer_charge>[\.0-9]+)/ =~ line)
          # print sewer, sewer_rate, sewer_charge
          # puts line
          sewer_consumption_var += sewer.to_f
          sewer_rate_var += sewer_rate.to_f
          sewer_charge_var += sewer_charge.to_f
        end
      end
      if (status == :gas)
        if (/Gas charges from.*?(?<gas_charges>[\.0-9]+)$/ =~ line)
          gas_charges_var += gas_charges.to_f
        end
      end

      if (/Total Stormwater Rate Charges.*?(?<stormwater_charges>[\.0-9]+)/ =~ line)
        stormwater_charges_var += stormwater_charges.to_f
        puts stormwater_charges_var
        puts line
      end
      if (/Water Heater Rental Charges:\s+(?<water_heater>[\.0-9]+)$/ =~ line)
        water_heater_var = water_heater.to_f
        puts line
      end
    end
    puts "watercomsumption #{water_consumption_var}"
    # puts "water_rate #{water_rate_var}"
    puts "water #{water_charge_var}"
    puts "sewer_consumption #{sewer_consumption_var}"
    # puts sewer_rate_var
    puts "sewer #{sewer_charge_var}"
    puts "water overall #{water_charge_var + sewer_charge_var}"
    puts "gas #{gas_charges_var}"
    puts "stormwater #{stormwater_charges_var}"
    puts "water heater #{water_heater_var}"
    puts "date: #{statement_date}, summary: $#{water_charge_var+sewer_charge_var+gas_charges_var+stormwater_charges_var+water_heater_var}"
  end
end

if $0 == __FILE__
  text_files = ARGV.empty? ? Dir['**/*.txt'] : ARGV
  STDERR.puts "files: #{text_files}" if $VERBOSE

  text_files.sort.each do |invoice|
    process_invoice_text(invoice)
  end
end

