export interface PartStock {
  part_type_name: string;
  total_produced: number;
  used_count: number;
  stock_count: number;
}

// Uçak modeline göre parça stok bilgisi
export interface AircraftPartStock {
  aircraft_model_name: string;
  parts: PartStock[];
}
