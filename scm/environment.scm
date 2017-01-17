;;;;; 对环境的操作
;; 将环境表示为一个框架的表，一个环境的外围环境就是这个表的cdr，空环境用空表表示
(define the-empty-environment '())

(define (first-frame env) (car env))

(define (enclosing-environment env) (cdr env))

;; 在环境中的每个框架都是一对表形成的序对：一个表存储这一框架的所有变量的表，另一个表存放对应的约束值
(define (make-frame variables values)
  (cons variables values))

(define (frame-variables frame) (car frame))

(define (fram-values frame) (cdr frame))

;; 将变量与约束值存入当前框架
(define (add-binding-to-frame! var val frame)
  (set-car! frame (cons var (car frame)))
  (set-cdr! frame (cons val (cdr frame))))

;; 扩充一个环境
(define (extend-environment vars vals base-env)
  (if (= (length vars) (length vals))
      (cons (make-frame vars vals) base-env)
      (if (< (length vars) (length vals))
          (error "Too many arguments supplied" vars vals)
          (error "Too few arguments supplied" vars vals))))

;; 寻找一个变量
(define (lookup-variable-value var env)
  (define (env-loop env)
    (define (scan vars vals)
      (cond ((null? vars)
             (env-loop (enclosing-environment env)))
            ((eq? var (car vars))
             (car vals))
            (else (scan (cdr vars) (cdr vals)))))
    (if (eq? env the-empty-environment)
        (error "Unbound variable" var)
        (let ([frame (first-frame env)])
          (scan (frame-variables frame)
                (fram-values frame)))))
  (env-loop env))

;; 为变量设置新值
(define (set-variable-value! var val env)
  (define (env-loop env)
    (define (scan vars vals)
      (cond ((null? vars)
             (env-loop (enclosing-environment env)))
            ((eq? var (car vars))
             (set-car! vals val))
            (else (scan (cdr vars) (cdr vals)))))
    (if (eq? env the-empty-environment)
        (error "Unbound variable -- SET!" var)
        (let ([frame (first-frame env)])
          (scan (frame-variables frame)
                (fram-values frame)))))
  (env-loop env))

;; 定义一个变量
(define (define-variable! var val env)
  (let ([frame (first-frame env)])
    (define (scan vars vals)
      (cond ((null? vars)
             (add-binding-to-frame! var val frame))
            ((eq? var (car vars))
             (set-car! vals val))
            (else (scan (cdr vars) (cdr vals)))))
    (scan (frame-variables frame)
          (fram-values frame))))
