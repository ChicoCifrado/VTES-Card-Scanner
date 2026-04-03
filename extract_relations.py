#!/usr/bin/env python3
"""
Extraer relaciones de cartas VTES: equipos, retainers, títulos, variants
Genera card_relations.json
"""
import json
import sys

def extract_relations(vtes_path, output_path):
    with open(vtes_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    
    # Estructura con todos los campos
    relations = {
        "version": "1.0",
        "total_cards": len(cards),
        "relations": {
            "equipos": [],
            "retainers": [],
            "variants": [],
            "titulos": [],
            "clans_rare": [],
        },
        "metadata": {
            "source": "KRCG V2",
            "generated_by": "extract_relations.py",
        },
    }
    
    for card in cards:
        card_id = card.get('id')
        card_name = card.get('printed_name', card.get('_name', ''))
        group = card.get('group', 0)
        capacity = card.get('capacity', 0)
        disciplines = card.get('disciplines', [])
        title = card.get('title', '')
        variants = card.get('variants', {})
        has_advanced = card.get('has_advanced', False)
        clans = card.get('clans', [])
        
        # 1. Equipos (Inner Circle, Baron, etc.)
        if title in ['Inner Circle', 'Baron', 'Primogen', 'Archbishop', 'Methuselah']:
            relations['relations']['equipos'].append({
                "id": card_id,
                "name": card_name,
                "title": title,
                "group": group,
                "capacity": capacity,
                "clans": clans,
            })
        
        # 2. Retainers (capacity bajo 1-4)
        if 1 <= capacity <= 4 and disciplines:
            if card_id not in [v.get('id', '') for v in relations['relations']['retainers']]:
                relations['relations']['retainers'].append({
                    "id": card_id,
                    "name": card_name,
                    "capacity": capacity,
                    "group": group,
                    "clans": clans,
                })
        
        # 3. Variants
        if variants:
            for variant_id, variant_name in variants.items():
                relations['relations']['variants'].append({
                    "original": {
                        "id": card_id,
                        "name": card_name,
                        "group": group,
                        "base": variants.get('G2') or variants.get('G1') or variants.get('G3')
                    },
                    "variant": {
                        "id": variant_id,
                        "name": variant_name,
                        "type": "Advanced" if has_advanced else "Alternate"
                    }
                })
        
        # 4. Títulos especiales
        if title:
            relations['relations']['titulos'].append({
                "id": card_id,
                "name": card_name,
                "title": title,
                "group": group,
                "capacity": capacity
            })
        
        # 5. Clans raros
        rare_clans = ['Caitiff', 'Sabat', 'Ventrue antitribu', 'Malkavian antitribu', 
                      'Tremere antitribu', 'Nosferatu antitribu', 'Giovanni antitribu',
                      'Ministry antitribu', 'Ishtarri', 'Osebo', 'Akunanse', 'Ahrimane',
                      'Blood Brother', 'Gargoyle', 'Harbinger of Skulls']
        if any(rc in clans for rc in rare_clans):
            relations['relations']['clans_rare'].append({
                "id": card_id,
                "name": card_name,
                "clans": clans,
                "capacity": capacity,
                "group": group
            })
    
    # Ordenar
    for key in relations['relations']:
        relations['relations'][key].sort(key=lambda x: x.get('name', ''))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(relations, f, indent=2, ensure_ascii=False)
    
    stats = {
        "equipos": len(relations['relations']['equipos']),
        "retainers": len(relations['relations']['retainers']),
        "variants": len(relations['relations']['variants']),
        "titulos": len(relations['relations']['titulos']),
        "clans_rare": len(relations['relations']['clans_rare']),
        "total": sum([
            len(relations['relations']['equipos']),
            len(relations['relations']['retainers']),
            len(relations['relations']['variants']),
            len(relations['relations']['titulos']),
            len(relations['relations']['clans_rare'])
        ])
    }
    
    print(f"✅ Relaciones extraídas:")
    print(f"   Equipos: {stats['equipos']}")
    print(f"   Retainers: {stats['retainers']}")
    print(f"   Variants: {stats['variants']}")
    print(f"   Títulos: {stats['titulos']}")
    print(f"   Clans raros: {stats['clans_rare']}")
    print(f"   Total: {stats['total']}")
    print(f"\n📄 Guardado en: {output_path}")
    
    return stats

if __name__ == '__main__':
    vtes_file = sys.argv[1] if len(sys.argv) > 1 else 'vtes.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'card_relations.json'
    
    print(f"\n🔍 Procesando {vtes_file}...")
    print(f"🎯 Generando {output_file}...")
    print()
    
    stats = extract_relations(vtes_file, output_file)
    
    print(f"\n✅ ¡Completado!")
    print(f"   Total cartas procesadas: {stats['total']}")
