# IDL v2 Syntax Reference

Source of truth: [docs/idl-v2-spec.md](../../docs/idl-v2-spec.md).

## Annotations

### Global

File-level metadata, must appear at the start of the file:

- `!@sails: 0.1.0` — IDL version
- `!@author: me` — author
- `!@git: ...` — source code URL
- `!@version: 0.2.0` — protocol version

### Include

- `!@include: <path_to_idl>` — include another IDL file
- `!@include: git://github.com/org/repo/file.idl` — include from git URL
- Includes are deduplicated by source ID. Circular includes are prevented.

### Local

Annotations placed above the related token:

- `@query` — marks read-only functions
- `@partial` — partial service subset (requires explicit `interface_id`)
- `@entry-id: <number>` — override automatic positional index
- `@indexed` — marks indexed event fields
- `@doc: text` (shortcut: `///`) — documentation

## Types

### Primitives

`bool`, `char`, `String`, `u8`–`u128`, `i8`–`i128`

### Collections

- `[T]` — dynamic-length array (slice)
- `[T; N]` — fixed-length array
- `(T1, T2, ..)` — tuple
- `()` — unit type

### Structs

```rust
struct Named { f1: u64, f2: Type2 }    // named fields
struct Tuple(Type1, Type2);             // tuple-like
struct Unit;                            // unit-like
```

### Enums

```rust
enum Type {
    Var1 { f1: Type1, f2: Type2 },  // struct-like
    Var2,                            // unit-like
    Var3(Type3),                     // tuple-like
}
```

### Generics

```rust
struct Point<T> { x: T, y: T }
enum Result<T, E> { Ok(T), Err(E) }
```

### Built-in Aliases

`actor` = `ActorId([u8; 32])`, `code` = `CodeId([u8; 32])`, `u256` = `U256([u64; 4])`, `h160` = `H160([u8; 20])`, `h256` = `H256([u8; 32])`, `map<K,V>` = `[(K,V)]`, `set<T>` = `[T]`

## Service

```
service <ident> [@0x<interface_id>] {
    extends { Base1, Base2 }
    events { ... }
    functions { ... }
    types { ... }
}
```

### Functions

```
/// Documentation
[@query]
[@entry-id: N]
FuncName(param1: Type1, param2: Type2) [-> ReturnType] [throws ErrorType];
```

- `@query` — read-only, no state mutation
- `@entry-id: N` — override automatic positional index (starts from 0)
- `throws <Type>` — explicit error type

### Events

Modeled as enum variants inside `events { ... }`:

```
events {
    StatusChanged(Point<u32>),
    Jubilee { amount: u64, bits: bitvec },
    Simple,
}
```

- `@entry-id: N` overrides automatic event index

### Partial Services

For generating a client targeting specific methods of a large contract:

```
@partial
service PartialService@0x1234567890abcdef {
    events {
        @entry-id: 2
        SomethingHappened(String);
    }
    functions {
        @entry-id: 5
        SomeMethod() -> bool;
    }
}
```

Requires explicit `interface_id` and `entry_id` on each member.

## Program

```
program <ident> {
    constructors {
        Create();
        WithOwner(owner: actor) throws ZeroOwnerError;
    }
    services {
        Canvas: Canvas;
        DemoCanvas: Canvas;
    }
    types { ... }
}
```

## Full Example

```
!@sails: 0.1.0
!@include: ownable.idl

/// Canvas service
service Canvas {
    extends { Ownable, Pausable }

    events {
        StatusChanged(Point<u32>),
        Jubilee { @indexed amount: u64, bits: bitvec },
    }

    functions {
        ColorPoint(point: Point<u32>, color: Color) throws ColorError;
        KillPoint(point: Point<u32>) -> bool throws String;
        @query
        Points(offset: u32, len: u32) -> map<Point<u32>, PointStatus> throws String;
        @query
        PointStatus(point: Point<u32>) -> Option<PointStatus>;
    }

    types {
        struct Color { color: [u8; 4], space: ColorSpace }
        enum ColorError { InvalidSource, DeadPoint }
        struct Point<T> { x: T, y: T }
    }
}
```
