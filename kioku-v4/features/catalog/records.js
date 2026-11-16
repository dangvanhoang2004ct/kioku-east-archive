// Product-line references from official maker sites, paired with ORIGINAL editorial photography.
// None of these are KIOKU physical inventory. No price, availability, grading, or authenticity claims.
export const REFERENCES = [
  {
    "slug": "ichiban-kuji",
    "maker": "Bandai Spirits",
    "line": "Ichiban Kuji",
    "title": "Prize figure archive",
    "category": "Prize lines",
    "status": "Editorial study \u2014 no stock",
    "image": "./assets/img/editorial-1-1.webp",
    "series": "Anime figures",
    "rank": 0
  },
  {
    "slug": "banpresto",
    "maker": "Bandai Spirits",
    "line": "Banpresto",
    "title": "Everyday icons",
    "category": "Display figures",
    "status": "Editorial study \u2014 no stock",
    "image": "./assets/img/editorial-2-1.webp",
    "series": "Anime figures",
    "rank": 1
  },
  {
    "slug": "ichibansho",
    "maker": "Bandai Spirits",
    "line": "Ichibansho",
    "title": "Objects in motion",
    "category": "Display figures",
    "status": "Editorial study \u2014 no stock",
    "image": "./assets/img/editorial-1-2.webp",
    "series": "Anime figures",
    "rank": 2
  },
  {
    "slug": "pop",
    "maker": "MegaHouse",
    "line": "Portrait.Of.Pirates",
    "title": "A scene remembered",
    "category": "Portrait series",
    "status": "Editorial study \u2014 no stock",
    "image": "./assets/img/editorial-2-2.webp",
    "series": "Anime figures",
    "rank": 3
  },
  {
    "slug": "lookup",
    "maker": "MegaHouse",
    "line": "Lookup",
    "title": "A familiar expression",
    "category": "Figure series",
    "status": "Editorial study \u2014 no stock",
    "image": "./assets/img/editorial-1-1.webp",
    "series": "Anime figures",
    "rank": 4
  },
  {
    "slug": "gem",
    "maker": "MegaHouse",
    "line": "G.E.M. Series",
    "title": "The held expression",
    "category": "Figure series",
    "status": "Editorial study \u2014 no stock",
    "image": "./assets/img/editorial-2-1.webp",
    "series": "Anime figures",
    "rank": 5
  }
];
export const findReference=(slug)=>REFERENCES.find(x=>x.slug===slug);
